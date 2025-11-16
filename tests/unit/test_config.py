"""ConfigManager 单元测试"""

import pytest
import os
from pathlib import Path
from src.core.config import ConfigManager, ConfigError, SpiderConfig


class TestSpiderConfig:
    """测试 SpiderConfig 数据类"""

    def test_default_values(self):
        """测试默认配置值"""
        config = SpiderConfig(cookies="test_cookies")
        
        assert config.cookies == "test_cookies"
        assert config.rate_limit == 3.0
        assert config.retry_times == 3
        assert config.timeout == 30
        assert config.proxy is None
        assert config.log_level == "INFO"
        assert config.output_dir == "datas"
        assert config.enable_resume is True
        assert config.download_media is True

    def test_custom_values(self):
        """测试自定义配置值"""
        config = SpiderConfig(
            cookies="custom_cookies",
            rate_limit=5.0,
            retry_times=5,
            timeout=60,
            proxy={"http": "http://proxy:8080"},
            log_level="DEBUG"
        )
        
        assert config.cookies == "custom_cookies"
        assert config.rate_limit == 5.0
        assert config.retry_times == 5
        assert config.timeout == 60
        assert config.proxy == {"http": "http://proxy:8080"}
        assert config.log_level == "DEBUG"


class TestConfigManager:
    """测试 ConfigManager 配置管理器"""

    def test_init_without_env_file(self, tmp_path):
        """测试在没有.env文件时初始化"""
        os.chdir(tmp_path)
        manager = ConfigManager(env_file=".env")
        assert manager.env_file == ".env"
        assert manager._config is None

    def test_load_config_from_env(self, monkeypatch):
        """测试从环境变量加载配置"""
        monkeypatch.setenv("COOKIES", "test_cookies_123")
        monkeypatch.setenv("RATE_LIMIT", "5.0")
        monkeypatch.setenv("RETRY_TIMES", "5")
        monkeypatch.setenv("TIMEOUT", "60")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        manager = ConfigManager()
        config = manager.load_config()
        
        assert config.cookies == "test_cookies_123"
        assert config.rate_limit == 5.0
        assert config.retry_times == 5
        assert config.timeout == 60
        assert config.log_level == "DEBUG"

    def test_load_config_with_proxy(self, monkeypatch):
        """测试加载代理配置"""
        monkeypatch.setenv("COOKIES", "test_cookies")
        monkeypatch.setenv("HTTP_PROXY", "http://proxy:8080")
        monkeypatch.setenv("HTTPS_PROXY", "https://proxy:8443")
        
        manager = ConfigManager()
        config = manager.load_config()
        
        assert config.proxy is not None
        assert config.proxy["http"] == "http://proxy:8080"
        assert config.proxy["https"] == "https://proxy:8443"

    def test_validate_config_missing_cookies(self):
        """测试验证缺失Cookie配置"""
        manager = ConfigManager()
        config = SpiderConfig(cookies="")
        
        with pytest.raises(ConfigError) as exc_info:
            manager.validate_config(config)
        
        assert "Cookie配置缺失" in str(exc_info.value)

    def test_validate_config_invalid_cookies(self):
        """测试验证无效Cookie配置"""
        manager = ConfigManager()
        config = SpiderConfig(cookies="your_cookies_here")
        
        with pytest.raises(ConfigError) as exc_info:
            manager.validate_config(config)
        
        assert "Cookie配置缺失或无效" in str(exc_info.value)

    def test_validate_config_invalid_rate_limit(self):
        """测试验证无效速率限制"""
        manager = ConfigManager()
        config = SpiderConfig(cookies="valid_cookies", rate_limit=0)
        
        with pytest.raises(ConfigError) as exc_info:
            manager.validate_config(config)
        
        assert "速率限制必须大于0" in str(exc_info.value)

    def test_validate_config_negative_retry_times(self):
        """测试验证负数重试次数"""
        manager = ConfigManager()
        config = SpiderConfig(cookies="valid_cookies", retry_times=-1)
        
        with pytest.raises(ConfigError) as exc_info:
            manager.validate_config(config)
        
        assert "重试次数不能为负数" in str(exc_info.value)

    def test_validate_config_invalid_timeout(self):
        """测试验证无效超时时间"""
        manager = ConfigManager()
        config = SpiderConfig(cookies="valid_cookies", timeout=0)
        
        with pytest.raises(ConfigError) as exc_info:
            manager.validate_config(config)
        
        assert "超时时间必须大于0" in str(exc_info.value)

    def test_validate_config_invalid_log_level(self):
        """测试验证无效日志级别"""
        manager = ConfigManager()
        config = SpiderConfig(cookies="valid_cookies", log_level="INVALID")
        
        with pytest.raises(ConfigError) as exc_info:
            manager.validate_config(config)
        
        assert "无效的日志级别" in str(exc_info.value)

    def test_validate_config_valid(self):
        """测试验证有效配置"""
        manager = ConfigManager()
        config = SpiderConfig(cookies="valid_cookies")
        
        result = manager.validate_config(config)
        assert result is True

    def test_get_with_default(self, monkeypatch):
        """测试获取配置项（使用默认值）"""
        manager = ConfigManager()
        
        value = manager.get("NON_EXISTENT_KEY", "default_value")
        assert value == "default_value"

    def test_get_existing_key(self, monkeypatch):
        """测试获取已存在的配置项"""
        monkeypatch.setenv("TEST_KEY", "test_value")
        
        manager = ConfigManager()
        value = manager.get("TEST_KEY")
        assert value == "test_value"

    def test_config_property(self, monkeypatch):
        """测试config属性"""
        monkeypatch.setenv("COOKIES", "test_cookies")
        
        manager = ConfigManager()
        assert manager.config is None
        
        config = manager.load_config()
        assert manager.config is not None
        assert manager.config.cookies == "test_cookies"

    def test_load_config_type_conversion_error(self, monkeypatch):
        """测试配置类型转换错误"""
        monkeypatch.setenv("COOKIES", "test_cookies")
        monkeypatch.setenv("RATE_LIMIT", "invalid_number")
        
        manager = ConfigManager()
        
        with pytest.raises(ConfigError) as exc_info:
            manager.load_config()
        
        assert "配置格式错误" in str(exc_info.value)

    def test_validate_config_invalid_max_concurrent_downloads(self):
        """测试验证无效的最大并发下载数"""
        manager = ConfigManager()
        config = SpiderConfig(cookies="valid_cookies", max_concurrent_downloads=0)
        
        with pytest.raises(ConfigError) as exc_info:
            manager.validate_config(config)
        
        assert "最大并发下载数必须大于0" in str(exc_info.value)

    def test_load_config_boolean_conversion(self, monkeypatch):
        """测试布尔值配置转换"""
        monkeypatch.setenv("COOKIES", "test_cookies")
        monkeypatch.setenv("ENABLE_RESUME", "false")
        monkeypatch.setenv("DOWNLOAD_MEDIA", "False")
        
        manager = ConfigManager()
        config = manager.load_config()
        
        assert config.enable_resume is False
        assert config.download_media is False
