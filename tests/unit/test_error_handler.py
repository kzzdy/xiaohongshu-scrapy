"""ErrorHandler 单元测试"""

import pytest
import time
from pathlib import Path
from src.core.error_handler import (
    ErrorHandler,
    SpiderError,
    ConfigError,
    NetworkError,
    APIError,
    DataError,
    RateLimitError
)


class TestSpiderError:
    """测试 SpiderError 异常类"""

    def test_spider_error_basic(self):
        """测试基础异常"""
        error = SpiderError("测试错误")
        
        assert error.message == "测试错误"
        assert error.details == {}
        assert str(error) == "测试错误"

    def test_spider_error_with_details(self):
        """测试带详情的异常"""
        error = SpiderError("测试错误", details={"url": "http://test.com", "code": 404})
        
        assert error.message == "测试错误"
        assert error.details == {"url": "http://test.com", "code": 404}
        assert "url=http://test.com" in str(error)
        assert "code=404" in str(error)


class TestErrorHandler:
    """测试 ErrorHandler 错误处理器"""

    @pytest.fixture
    def handler(self, tmp_path):
        """创建错误处理器实例"""
        log_dir = tmp_path / "logs"
        return ErrorHandler(log_level="INFO", log_dir=str(log_dir))

    def test_init(self, tmp_path):
        """测试初始化"""
        log_dir = tmp_path / "logs"
        handler = ErrorHandler(log_level="DEBUG", log_dir=str(log_dir))
        
        assert handler.log_level == "DEBUG"
        assert handler.log_dir == log_dir
        assert log_dir.exists()

    def test_retry_on_error_success(self, handler):
        """测试重试装饰器 - 成功情况"""
        call_count = 0
        
        @handler.retry_on_error(max_retries=3)
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert call_count == 1

    def test_retry_on_error_with_retries(self, handler):
        """测试重试装饰器 - 需要重试"""
        call_count = 0
        
        @handler.retry_on_error(max_retries=3, delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("网络错误")
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert call_count == 3

    def test_retry_on_error_max_retries_exceeded(self, handler):
        """测试重试装饰器 - 超过最大重试次数"""
        call_count = 0
        
        @handler.retry_on_error(max_retries=2, delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1
            raise NetworkError("持续网络错误")
        
        with pytest.raises(NetworkError):
            test_func()
        
        assert call_count == 3  # 初始调用 + 2次重试

    def test_retry_on_error_specific_exception(self, handler):
        """测试重试装饰器 - 特定异常类型"""
        call_count = 0
        
        @handler.retry_on_error(max_retries=3, exceptions=(NetworkError,), delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise NetworkError("网络错误")
            elif call_count == 2:
                raise ValueError("其他错误")
            return "success"
        
        # ValueError不在重试列表中，应该直接抛出
        with pytest.raises(ValueError):
            test_func()
        
        assert call_count == 2

    def test_retry_on_error_backoff(self, handler):
        """测试重试装饰器 - 指数退避"""
        call_times = []
        
        @handler.retry_on_error(max_retries=3, delay=0.1, backoff=2.0)
        def test_func():
            call_times.append(time.time())
            raise NetworkError("网络错误")
        
        with pytest.raises(NetworkError):
            test_func()
        
        # 验证延迟时间递增
        assert len(call_times) == 4  # 初始 + 3次重试
        
        # 第一次重试延迟约0.1秒
        delay1 = call_times[1] - call_times[0]
        assert 0.08 < delay1 < 0.15
        
        # 第二次重试延迟约0.2秒
        delay2 = call_times[2] - call_times[1]
        assert 0.18 < delay2 < 0.25

    def test_handle_api_error_basic(self, handler):
        """测试处理API错误 - 基础情况"""
        error = APIError("API请求失败")
        url = "https://api.example.com/test"
        
        error_info = handler.handle_api_error(error, url)
        
        assert error_info["url"] == url
        assert error_info["error_type"] == "APIError"
        assert error_info["error_message"] == "API请求失败"
        assert "timestamp" in error_info

    def test_handle_api_error_with_response(self, handler):
        """测试处理API错误 - 带响应对象"""
        error = APIError("API请求失败")
        url = "https://api.example.com/test"
        
        # 模拟响应对象
        class MockResponse:
            status_code = 404
            text = "Not Found"
        
        response = MockResponse()
        error_info = handler.handle_api_error(error, url, response)
        
        assert error_info["status_code"] == 404
        assert error_info["response_preview"] == "Not Found"

    def test_handle_api_error_rate_limit(self, handler):
        """测试处理API错误 - 速率限制"""
        error = RateLimitError("请求过于频繁")
        url = "https://api.example.com/test"
        
        class MockResponse:
            status_code = 429
            text = "Too Many Requests"
        
        response = MockResponse()
        error_info = handler.handle_api_error(error, url, response)
        
        assert error_info["status_code"] == 429
        assert error_info["recoverable"] is True
        assert "降低请求速率" in error_info["suggestion"]

    def test_handle_api_error_server_error(self, handler):
        """测试处理API错误 - 服务器错误"""
        error = APIError("服务器错误")
        url = "https://api.example.com/test"
        
        class MockResponse:
            status_code = 500
            text = "Internal Server Error"
        
        response = MockResponse()
        error_info = handler.handle_api_error(error, url, response)
        
        assert error_info["status_code"] == 500
        assert error_info["recoverable"] is True
        assert "稍后重试" in error_info["suggestion"]

    def test_handle_api_error_auth_error(self, handler):
        """测试处理API错误 - 认证错误"""
        error = APIError("认证失败")
        url = "https://api.example.com/test"
        
        class MockResponse:
            status_code = 401
            text = "Unauthorized"
        
        response = MockResponse()
        error_info = handler.handle_api_error(error, url, response)
        
        assert error_info["status_code"] == 401
        assert "Cookie" in error_info["suggestion"]

    def test_handle_api_error_timeout(self, handler):
        """测试处理API错误 - 超时"""
        error = NetworkError("Connection timeout")
        url = "https://api.example.com/test"
        
        error_info = handler.handle_api_error(error, url)
        
        assert error_info["recoverable"] is True
        assert "超时" in error_info["suggestion"]

    def test_create_error_report_empty(self, handler):
        """测试创建错误报告 - 空列表"""
        report = handler.create_error_report([])
        
        assert "无错误记录" in report

    def test_create_error_report_with_errors(self, handler):
        """测试创建错误报告 - 包含错误"""
        errors = [
            {
                "timestamp": "2024-01-01 12:00:00",
                "error_type": "NetworkError",
                "url": "https://api.example.com/test",
                "status_code": 500,
                "error_message": "服务器错误",
                "suggestion": "稍后重试",
                "recoverable": True
            },
            {
                "timestamp": "2024-01-01 12:01:00",
                "error_type": "APIError",
                "url": "https://api.example.com/test2",
                "error_message": "请求失败",
                "recoverable": False
            }
        ]
        
        report = handler.create_error_report(errors)
        
        assert "错误报告" in report
        assert "错误 #1" in report
        assert "错误 #2" in report
        assert "NetworkError" in report
        assert "APIError" in report
        assert "总计: 2 个错误" in report

    def test_suggest_recovery_action_rate_limit(self, handler):
        """测试建议恢复操作 - 速率限制"""
        error_info = {"recoverable": True, "status_code": 429}
        
        action = handler.suggest_recovery_action(error_info)
        
        assert action == "wait_and_retry"

    def test_suggest_recovery_action_server_error(self, handler):
        """测试建议恢复操作 - 服务器错误"""
        error_info = {"recoverable": True, "status_code": 500}
        
        action = handler.suggest_recovery_action(error_info)
        
        assert action == "retry_with_backoff"

    def test_suggest_recovery_action_timeout(self, handler):
        """测试建议恢复操作 - 超时"""
        error_info = {"recoverable": True, "error_type": "TimeoutError"}
        
        action = handler.suggest_recovery_action(error_info)
        
        assert action == "increase_timeout"

    def test_suggest_recovery_action_not_recoverable(self, handler):
        """测试建议恢复操作 - 不可恢复"""
        error_info = {"recoverable": False}
        
        action = handler.suggest_recovery_action(error_info)
        
        assert action is None

    def test_is_recoverable_error_network(self, handler):
        """测试判断可恢复错误 - 网络错误"""
        error = NetworkError("网络连接失败")
        
        assert handler.is_recoverable_error(error) is True

    def test_is_recoverable_error_rate_limit(self, handler):
        """测试判断可恢复错误 - 速率限制"""
        error = RateLimitError("请求过于频繁")
        
        assert handler.is_recoverable_error(error) is True

    def test_is_recoverable_error_config(self, handler):
        """测试判断可恢复错误 - 配置错误"""
        error = ConfigError("配置错误")
        
        assert handler.is_recoverable_error(error) is False

    def test_is_recoverable_error_by_message(self, handler):
        """测试判断可恢复错误 - 根据消息"""
        error1 = Exception("Connection timeout")
        error2 = Exception("Too many requests")
        error3 = Exception("Invalid configuration")
        
        assert handler.is_recoverable_error(error1) is True
        assert handler.is_recoverable_error(error2) is True
        assert handler.is_recoverable_error(error3) is False

    def test_log_methods(self, handler):
        """测试日志方法"""
        # 这些方法主要是记录日志，不抛出异常即可
        handler.log_info("信息日志")
        handler.log_warning("警告日志")
        handler.log_error("错误日志")
        handler.log_debug("调试日志")
        handler.log_error("错误日志", Exception("测试异常"))

    def test_handle_fatal_error(self, handler):
        """测试处理致命错误"""
        error = Exception("致命错误")
        
        # 不应该抛出异常
        handler.handle_fatal_error(error, "系统崩溃")
