"""配置管理器模块"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import os
from dotenv import load_dotenv


class ConfigError(Exception):
    """配置错误异常"""

    pass


@dataclass
class SpiderConfig:
    """爬虫配置数据类"""

    cookies: str
    rate_limit: float = 3.0
    retry_times: int = 3
    timeout: int = 30
    proxy: Optional[Dict[str, str]] = None
    log_level: str = "INFO"
    output_dir: str = "datas"
    progress_file: str = "datas/.progress.json"
    enable_resume: bool = True
    download_media: bool = True
    max_concurrent_downloads: int = 3


class ConfigManager:
    """配置管理器

    负责加载和管理所有配置信息，支持从环境变量和.env文件加载配置
    """

    def __init__(self, env_file: str = ".env"):
        """初始化配置管理器

        Args:
            env_file: 环境变量文件路径，默认为.env
        """
        self.env_file = env_file
        self._config: Optional[SpiderConfig] = None
        self._load_env()

    def _load_env(self) -> None:
        """加载环境变量文件"""
        env_path = Path(self.env_file)
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # 如果.env文件不存在，尝试从系统环境变量加载
            pass

    def load_config(self) -> SpiderConfig:
        """加载配置

        Returns:
            SpiderConfig: 配置对象

        Raises:
            ConfigError: 配置加载或验证失败时抛出
        """
        try:
            # 加载必填配置
            cookies = self.get("COOKIES", "")

            # 加载可选配置
            rate_limit = float(self.get("RATE_LIMIT", "3.0"))
            retry_times = int(self.get("RETRY_TIMES", "3"))
            timeout = int(self.get("TIMEOUT", "30"))
            log_level = self.get("LOG_LEVEL", "INFO")
            output_dir = self.get("OUTPUT_DIR", "datas")
            progress_file = self.get("PROGRESS_FILE", "datas/.progress.json")
            enable_resume = self.get("ENABLE_RESUME", "true").lower() == "true"
            download_media = self.get("DOWNLOAD_MEDIA", "true").lower() == "true"
            max_concurrent_downloads = int(self.get("MAX_CONCURRENT_DOWNLOADS", "3"))

            # 加载代理配置
            proxy = None
            http_proxy = self.get("HTTP_PROXY")
            https_proxy = self.get("HTTPS_PROXY")
            if http_proxy or https_proxy:
                proxy = {}
                if http_proxy:
                    proxy["http"] = http_proxy
                if https_proxy:
                    proxy["https"] = https_proxy

            config = SpiderConfig(
                cookies=cookies,
                rate_limit=rate_limit,
                retry_times=retry_times,
                timeout=timeout,
                proxy=proxy,
                log_level=log_level,
                output_dir=output_dir,
                progress_file=progress_file,
                enable_resume=enable_resume,
                download_media=download_media,
                max_concurrent_downloads=max_concurrent_downloads,
            )

            # 验证配置
            self.validate_config(config)

            self._config = config
            return config

        except ValueError as e:
            raise ConfigError(f"配置格式错误: {str(e)}")
        except Exception as e:
            raise ConfigError(f"配置加载失败: {str(e)}")

    def validate_config(self, config: SpiderConfig) -> bool:
        """验证配置有效性

        Args:
            config: 配置对象

        Returns:
            bool: 配置是否有效

        Raises:
            ConfigError: 配置验证失败时抛出
        """
        # 验证必填项
        if not config.cookies or config.cookies == "your_cookies_here":
            raise ConfigError(
                "Cookie配置缺失或无效！\n"
                "请按以下步骤配置：\n"
                "1. 复制 .env.example 文件为 .env\n"
                "2. 登录小红书网页版 (https://www.xiaohongshu.com)\n"
                "3. 打开浏览器开发者工具（F12）\n"
                "4. 在Network标签中找到任意请求，复制Cookie值\n"
                "5. 将Cookie值填入 .env 文件的 COOKIES 配置项"
            )

        # 验证速率限制
        if config.rate_limit <= 0:
            raise ConfigError(f"速率限制必须大于0，当前值: {config.rate_limit}")

        # 验证重试次数
        if config.retry_times < 0:
            raise ConfigError(f"重试次数不能为负数，当前值: {config.retry_times}")

        # 验证超时时间
        if config.timeout <= 0:
            raise ConfigError(f"超时时间必须大于0，当前值: {config.timeout}")

        # 验证日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config.log_level.upper() not in valid_log_levels:
            raise ConfigError(
                f"无效的日志级别: {config.log_level}\n" f"有效值: {', '.join(valid_log_levels)}"
            )

        # 验证并发下载数
        if config.max_concurrent_downloads <= 0:
            raise ConfigError(f"最大并发下载数必须大于0，当前值: {config.max_concurrent_downloads}")

        return True

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项

        Args:
            key: 配置项键名
            default: 默认值

        Returns:
            配置项的值，如果不存在则返回默认值
        """
        return os.getenv(key, default)

    @property
    def config(self) -> Optional[SpiderConfig]:
        """获取当前配置对象"""
        return self._config
