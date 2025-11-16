"""基础API客户端模块"""

from typing import Dict, Any, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler, NetworkError, APIError


class BaseAPIClient:
    """基础API客户端

    提供统一的HTTP请求接口，集成速率限制、错误处理和会话管理。
    所有具体的API客户端应继承此类。
    """

    def __init__(
        self,
        base_url: str,
        rate_limiter: RateLimiter,
        error_handler: ErrorHandler,
        timeout: int = 30,
        proxies: Optional[Dict[str, str]] = None,
    ):
        """初始化API客户端

        Args:
            base_url: API基础URL
            rate_limiter: 速率限制器实例
            error_handler: 错误处理器实例
            timeout: 请求超时时间（秒），默认30秒
            proxies: 代理配置，格式: {"http": "...", "https": "..."}
        """
        self.base_url = base_url.rstrip("/")
        self.rate_limiter = rate_limiter
        self.error_handler = error_handler
        self.timeout = timeout
        self.proxies = proxies
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """创建并配置HTTP会话

        配置连接池、重试策略等，提高请求效率和可靠性。
        优化连接池参数以提升性能和资源利用率。

        Returns:
            配置好的Session对象
        """
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔：1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
        )

        # 配置HTTP适配器 - 优化连接池参数
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,  # 增加连接池大小以支持更多并发
            pool_maxsize=50,  # 增加最大连接数
            pool_block=False,  # 不阻塞，连接池满时创建新连接
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def request(
        self, method: str, endpoint: str, **kwargs
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """发送HTTP请求

        统一的请求接口，自动处理速率限制、错误处理和响应解析。

        Args:
            method: HTTP方法（GET, POST等）
            endpoint: API端点路径
            **kwargs: 传递给requests的其他参数（headers, data, json, params等）

        Returns:
            元组 (success, message, data):
            - success: 请求是否成功
            - message: 成功或错误消息
            - data: 响应数据（JSON格式），失败时为None
        """
        # 应用速率限制
        self.rate_limiter.acquire()

        # 构建完整URL
        url = f"{self.base_url}{endpoint}" if not endpoint.startswith("http") else endpoint

        # 设置默认参数
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        if "proxies" not in kwargs and self.proxies:
            kwargs["proxies"] = self.proxies

        try:
            # 发送请求
            response = self.session.request(method, url, **kwargs)

            # 检查HTTP状态码
            response.raise_for_status()

            # 解析JSON响应
            try:
                res_json = response.json()
            except ValueError as e:
                self.error_handler.log_error(f"JSON解析失败: {url}", e)
                return False, f"响应格式错误: {str(e)}", None

            # 检查业务状态
            if isinstance(res_json, dict):
                success = res_json.get("success", True)
                msg = res_json.get("msg", "success" if success else "unknown error")

                if not success:
                    self.error_handler.log_warning(f"API业务错误: {url} - {msg}")
                    return False, msg, res_json

                return True, msg, res_json
            else:
                # 如果响应不是字典，直接返回
                return True, "success", res_json

        except requests.exceptions.Timeout as e:
            error_info = self.error_handler.handle_api_error(e, url)
            error_msg = f"请求超时: {url}"
            if error_info.get("suggestion"):
                error_msg += f" - {error_info['suggestion']}"
            return False, error_msg, None

        except requests.exceptions.ConnectionError as e:
            error_info = self.error_handler.handle_api_error(e, url)
            error_msg = f"连接失败: {url}"
            if error_info.get("suggestion"):
                error_msg += f" - {error_info['suggestion']}"
            return False, error_msg, None

        except requests.exceptions.HTTPError as e:
            error_info = self.error_handler.handle_api_error(e, url, e.response)
            error_msg = f"HTTP错误 {e.response.status_code}: {url}"
            if error_info.get("suggestion"):
                error_msg += f" - {error_info['suggestion']}"
            return False, error_msg, None

        except Exception as e:
            error_info = self.error_handler.handle_api_error(e, url)
            error_msg = f"请求失败: {str(e)}"
            if error_info.get("suggestion"):
                error_msg += f" - {error_info['suggestion']}"
            return False, error_msg, None

    def get(self, endpoint: str, **kwargs) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """发送GET请求

        Args:
            endpoint: API端点路径
            **kwargs: 传递给requests的其他参数

        Returns:
            元组 (success, message, data)
        """
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """发送POST请求

        Args:
            endpoint: API端点路径
            **kwargs: 传递给requests的其他参数

        Returns:
            元组 (success, message, data)
        """
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """发送PUT请求

        Args:
            endpoint: API端点路径
            **kwargs: 传递给requests的其他参数

        Returns:
            元组 (success, message, data)
        """
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """发送DELETE请求

        Args:
            endpoint: API端点路径
            **kwargs: 传递给requests的其他参数

        Returns:
            元组 (success, message, data)
        """
        return self.request("DELETE", endpoint, **kwargs)

    def download_file(
        self,
        url: str,
        filepath: str,
        chunk_size: int = 8192,
        **kwargs
    ) -> Tuple[bool, str]:
        """流式下载文件（优化大文件下载）

        使用流式下载避免将整个文件加载到内存中，适合下载大文件。

        Args:
            url: 文件URL
            filepath: 保存路径
            chunk_size: 每次读取的块大小（字节），默认8KB
            **kwargs: 传递给requests的其他参数

        Returns:
            元组 (success, message):
            - success: 下载是否成功
            - message: 成功或错误消息
        """
        # 应用速率限制
        self.rate_limiter.acquire()

        # 设置默认参数
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        if "proxies" not in kwargs and self.proxies:
            kwargs["proxies"] = self.proxies

        try:
            # 发送请求，启用流式传输
            kwargs["stream"] = True
            response = self.session.get(url, **kwargs)
            response.raise_for_status()

            # 流式写入文件
            from pathlib import Path
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # 过滤掉保持连接的空块
                        f.write(chunk)

            file_size = Path(filepath).stat().st_size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.2f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"

            return True, f"文件下载成功 ({size_str})"

        except requests.exceptions.Timeout as e:
            error_info = self.error_handler.handle_api_error(e, url)
            error_msg = f"下载超时: {url}"
            if error_info.get("suggestion"):
                error_msg += f" - {error_info['suggestion']}"
            return False, error_msg

        except requests.exceptions.ConnectionError as e:
            error_info = self.error_handler.handle_api_error(e, url)
            error_msg = f"连接失败: {url}"
            if error_info.get("suggestion"):
                error_msg += f" - {error_info['suggestion']}"
            return False, error_msg

        except requests.exceptions.HTTPError as e:
            error_info = self.error_handler.handle_api_error(e, url, e.response)
            error_msg = f"HTTP错误 {e.response.status_code}: {url}"
            if error_info.get("suggestion"):
                error_msg += f" - {error_info['suggestion']}"
            return False, error_msg

        except IOError as e:
            error_msg = f"文件写入失败: {filepath}"
            self.error_handler.log_error(error_msg, e)
            return False, error_msg

        except Exception as e:
            error_info = self.error_handler.handle_api_error(e, url)
            error_msg = f"下载失败: {str(e)}"
            if error_info.get("suggestion"):
                error_msg += f" - {error_info['suggestion']}"
            return False, error_msg

    def close(self) -> None:
        """关闭会话，释放资源"""
        if self.session:
            self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动关闭会话"""
        self.close()
