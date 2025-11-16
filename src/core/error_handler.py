"""错误处理器模块"""

from typing import Callable, Optional, Type, Tuple, Any
from functools import wraps
import time
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger


class SpiderError(Exception):
    """爬虫基础异常"""

    def __init__(self, message: str, details: Optional[dict] = None):
        """初始化异常
        
        Args:
            message: 错误消息
            details: 错误详情字典
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        """返回格式化的错误消息"""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigError(SpiderError):
    """配置错误"""
    pass


class NetworkError(SpiderError):
    """网络错误"""

    pass


class APIError(SpiderError):
    """API错误"""

    pass


class DataError(SpiderError):
    """数据错误"""

    pass


class RateLimitError(SpiderError):
    """速率限制错误"""
    pass


class ErrorHandler:
    """错误处理器

    统一处理和记录系统异常，提供重试机制和详细的错误日志。
    """

    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        """初始化错误处理器

        Args:
            log_level: 日志级别，默认INFO
            log_dir: 日志目录，默认logs
        """
        self.log_level = log_level.upper()
        self.log_dir = Path(log_dir)
        self._setup_logger()

    def _setup_logger(self) -> None:
        """配置日志系统

        配置两个日志文件：
        1. 普通日志：记录所有INFO及以上级别的日志，按天轮转，保留30天
        2. 错误日志：仅记录ERROR及以上级别的日志，按天轮转，保留30天
        
        日志轮转策略：
        - 每天午夜自动创建新日志文件
        - 自动压缩旧日志文件
        - 超过保留期的日志自动删除
        """
        # 创建日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 移除默认的logger配置
        logger.remove()

        # 添加控制台输出
        logger.add(
            sys.stderr,
            level=self.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
        )

        # 添加普通日志文件（按天轮转，保留30天，自动压缩）
        logger.add(
            self.log_dir / "spider_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # 每天午夜轮转
            retention="30 days",  # 保留30天
            compression="zip",  # 压缩旧日志
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            encoding="utf-8",
            enqueue=True,  # 异步写入，提高性能
        )

        # 添加错误日志文件（按天轮转，保留30天，仅记录ERROR及以上）
        logger.add(
            self.log_dir / "error_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # 每天午夜轮转
            retention="30 days",  # 保留30天
            compression="zip",  # 压缩旧日志
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
            encoding="utf-8",
            enqueue=True,  # 异步写入，提高性能
        )

        logger.info(f"日志系统初始化完成，日志级别: {self.log_level}")
        logger.info(f"日志目录: {self.log_dir.absolute()}")
        logger.info("日志轮转: 每天午夜，保留30天，自动压缩")

    def retry_on_error(
        self,
        max_retries: int = 3,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        delay: float = 1.0,
        backoff: float = 2.0,
    ) -> Callable:
        """重试装饰器

        当函数抛出指定异常时自动重试，支持指数退避。

        Args:
            max_retries: 最大重试次数，默认3次
            exceptions: 需要重试的异常类型元组，默认所有异常
            delay: 初始延迟时间（秒），默认1秒
            backoff: 退避系数，每次重试延迟时间乘以此系数，默认2.0

        Returns:
            装饰器函数

        Example:
            @error_handler.retry_on_error(max_retries=3, exceptions=(NetworkError,))
            def fetch_data():
                # 可能抛出NetworkError的代码
                pass
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay

                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e

                        if attempt < max_retries:
                            logger.warning(
                                f"函数 {func.__name__} 执行失败 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}"
                            )
                            logger.info(f"等待 {current_delay:.1f} 秒后重试...")
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(
                                f"函数 {func.__name__} 执行失败，已达到最大重试次数 ({max_retries + 1}): {str(e)}"
                            )

                # 所有重试都失败，抛出最后一个异常
                raise last_exception

            return wrapper

        return decorator

    def handle_api_error(
        self,
        error: Exception,
        url: str,
        response: Optional[Any] = None,
    ) -> dict:
        """处理API错误

        记录详细的API错误信息，包括URL、状态码、响应内容等，
        并返回结构化的错误信息用于错误恢复。

        Args:
            error: 异常对象
            url: 请求URL
            response: 响应对象（可选）
            
        Returns:
            包含错误详情的字典，用于错误恢复和分析
        """
        error_info = {
            "url": url,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recoverable": False,
            "suggestion": ""
        }
        
        error_msg = f"API请求失败: {url}"

        if response is not None:
            status_code = getattr(response, "status_code", "未知")
            error_info["status_code"] = status_code
            error_msg += f"\n状态码: {status_code}"
            
            # 根据状态码提供建议
            if status_code == 429:
                error_info["recoverable"] = True
                error_info["suggestion"] = "请求过于频繁，建议降低请求速率或稍后重试"
            elif status_code in [500, 502, 503, 504]:
                error_info["recoverable"] = True
                error_info["suggestion"] = "服务器错误，建议稍后重试"
            elif status_code == 401:
                error_info["suggestion"] = "认证失败，请检查Cookie是否有效"
            elif status_code == 403:
                error_info["suggestion"] = "访问被拒绝，可能需要更新Cookie或使用代理"
            elif status_code == 404:
                error_info["suggestion"] = "资源不存在，请检查URL是否正确"

            try:
                response_text = getattr(response, "text", "")
                if response_text:
                    # 限制响应内容长度
                    max_length = 500
                    if len(response_text) > max_length:
                        response_text = response_text[:max_length] + "..."
                    error_msg += f"\n响应内容: {response_text}"
                    error_info["response_preview"] = response_text
            except Exception:
                pass
        else:
            # 网络错误通常是可恢复的
            if "timeout" in str(error).lower():
                error_info["recoverable"] = True
                error_info["suggestion"] = "请求超时，建议检查网络连接或增加超时时间"
            elif "connection" in str(error).lower():
                error_info["recoverable"] = True
                error_info["suggestion"] = "连接失败，建议检查网络连接或使用代理"

        error_msg += f"\n错误信息: {str(error)}"
        
        if error_info["suggestion"]:
            error_msg += f"\n建议: {error_info['suggestion']}"

        logger.error(error_msg)
        
        return error_info

    def handle_fatal_error(self, error: Exception, message: str = "") -> None:
        """处理致命错误

        记录致命错误并优雅地终止程序。

        Args:
            error: 异常对象
            message: 附加错误消息
        """
        error_msg = "发生致命错误"
        if message:
            error_msg += f": {message}"

        logger.critical(error_msg)
        logger.exception(error)

        # 可以在这里添加通知逻辑（邮件、钉钉等）

        logger.info("程序即将退出...")

    def log_info(self, message: str) -> None:
        """记录信息日志"""
        logger.info(message)

    def log_warning(self, message: str) -> None:
        """记录警告日志"""
        logger.warning(message)

    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """记录错误日志

        Args:
            message: 错误消息
            exception: 异常对象（可选）
        """
        if exception:
            logger.error(f"{message}: {str(exception)}")
        else:
            logger.error(message)

    def log_debug(self, message: str) -> None:
        """记录调试日志"""
        logger.debug(message)
    
    def create_error_report(self, errors: list) -> str:
        """创建错误报告
        
        Args:
            errors: 错误信息列表
            
        Returns:
            格式化的错误报告字符串
        """
        if not errors:
            return "无错误记录"
        
        report = ["=" * 60, "错误报告", "=" * 60, ""]
        
        for i, error in enumerate(errors, 1):
            report.append(f"错误 #{i}")
            report.append(f"  时间: {error.get('timestamp', 'N/A')}")
            report.append(f"  类型: {error.get('error_type', 'N/A')}")
            report.append(f"  URL: {error.get('url', 'N/A')}")
            
            if 'status_code' in error:
                report.append(f"  状态码: {error['status_code']}")
            
            report.append(f"  消息: {error.get('error_message', 'N/A')}")
            
            if error.get('suggestion'):
                report.append(f"  建议: {error['suggestion']}")
            
            report.append(f"  可恢复: {'是' if error.get('recoverable') else '否'}")
            report.append("")
        
        report.extend(["=" * 60, f"总计: {len(errors)} 个错误", "=" * 60])
        
        return "\n".join(report)
    
    def suggest_recovery_action(self, error_info: dict) -> Optional[str]:
        """根据错误信息建议恢复操作
        
        Args:
            error_info: 错误信息字典
            
        Returns:
            恢复操作建议，如果无法恢复则返回None
        """
        if not error_info.get('recoverable'):
            return None
        
        status_code = error_info.get('status_code')
        error_type = error_info.get('error_type', '')
        
        # 根据错误类型提供具体的恢复建议
        if status_code == 429:
            return "wait_and_retry"  # 等待后重试
        elif status_code in [500, 502, 503, 504]:
            return "retry_with_backoff"  # 指数退避重试
        elif "timeout" in error_type.lower():
            return "increase_timeout"  # 增加超时时间
        elif "connection" in error_type.lower():
            return "check_network"  # 检查网络
        
        return "retry"  # 默认重试
    
    def is_recoverable_error(self, error: Exception) -> bool:
        """判断错误是否可恢复
        
        Args:
            error: 异常对象
            
        Returns:
            True表示可恢复，False表示不可恢复
        """
        # 网络相关错误通常可恢复
        recoverable_errors = (
            NetworkError,
            RateLimitError,
        )
        
        if isinstance(error, recoverable_errors):
            return True
        
        # 检查错误消息
        error_msg = str(error).lower()
        recoverable_keywords = [
            "timeout",
            "connection",
            "temporary",
            "retry",
            "rate limit",
            "too many requests"
        ]
        
        return any(keyword in error_msg for keyword in recoverable_keywords)
