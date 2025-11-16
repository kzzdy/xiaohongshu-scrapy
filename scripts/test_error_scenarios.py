#!/usr/bin/env python3
"""错误场景测试脚本

测试各种错误场景，验证错误处理和恢复机制是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.error_handler import (
    ErrorHandler,
    SpiderError,
    ConfigError,
    NetworkError,
    APIError,
    DataError,
    RateLimitError
)


def test_basic_exceptions():
    """测试基本异常类"""
    print("=" * 60)
    print("测试 1: 基本异常类")
    print("=" * 60)
    
    # 测试带详情的异常
    try:
        raise SpiderError("测试错误", {"code": 500, "url": "https://example.com"})
    except SpiderError as e:
        print(f"✓ SpiderError: {e}")
    
    # 测试不同类型的异常
    exceptions = [
        ConfigError("配置文件缺失", {"file": ".env"}),
        NetworkError("网络连接超时", {"timeout": 30}),
        APIError("API请求失败", {"status_code": 429}),
        DataError("数据验证失败", {"field": "note_id"}),
        RateLimitError("请求速率超限", {"limit": "3/s"})
    ]
    
    for exc in exceptions:
        print(f"✓ {type(exc).__name__}: {exc}")
    
    print()


def test_error_handler():
    """测试错误处理器"""
    print("=" * 60)
    print("测试 2: 错误处理器")
    print("=" * 60)
    
    handler = ErrorHandler(log_level="INFO")
    
    # 测试日志方法
    handler.log_info("这是一条信息日志")
    handler.log_warning("这是一条警告日志")
    handler.log_error("这是一条错误日志")
    handler.log_debug("这是一条调试日志（可能不显示）")
    
    print("✓ 日志方法测试完成")
    print()


def test_api_error_handling():
    """测试API错误处理"""
    print("=" * 60)
    print("测试 3: API错误处理")
    print("=" * 60)
    
    handler = ErrorHandler(log_level="INFO")
    
    # 模拟不同的API错误
    test_cases = [
        {
            "error": Exception("Connection timeout"),
            "url": "https://api.example.com/data",
            "response": None,
            "description": "连接超时"
        },
        {
            "error": Exception("Too many requests"),
            "url": "https://api.example.com/data",
            "response": type('obj', (object,), {
                'status_code': 429,
                'text': '{"error": "Rate limit exceeded"}'
            })(),
            "description": "速率限制"
        },
        {
            "error": Exception("Server error"),
            "url": "https://api.example.com/data",
            "response": type('obj', (object,), {
                'status_code': 500,
                'text': '{"error": "Internal server error"}'
            })(),
            "description": "服务器错误"
        },
        {
            "error": Exception("Unauthorized"),
            "url": "https://api.example.com/data",
            "response": type('obj', (object,), {
                'status_code': 401,
                'text': '{"error": "Invalid credentials"}'
            })(),
            "description": "认证失败"
        }
    ]
    
    errors = []
    for case in test_cases:
        print(f"\n测试场景: {case['description']}")
        error_info = handler.handle_api_error(
            case['error'],
            case['url'],
            case['response']
        )
        errors.append(error_info)
        
        print(f"  可恢复: {error_info.get('recoverable', False)}")
        print(f"  建议: {error_info.get('suggestion', 'N/A')}")
        
        # 测试恢复建议
        recovery = handler.suggest_recovery_action(error_info)
        if recovery:
            print(f"  恢复操作: {recovery}")
    
    # 生成错误报告
    print("\n" + "=" * 60)
    print("错误报告")
    print("=" * 60)
    report = handler.create_error_report(errors)
    print(report)
    
    print()


def test_error_recovery():
    """测试错误恢复机制"""
    print("=" * 60)
    print("测试 4: 错误恢复机制")
    print("=" * 60)
    
    handler = ErrorHandler(log_level="INFO")
    
    # 测试可恢复错误判断
    test_errors = [
        (NetworkError("Connection timeout"), True),
        (RateLimitError("Too many requests"), True),
        (ConfigError("Missing config"), False),
        (Exception("timeout occurred"), True),
        (Exception("connection refused"), True),
        (Exception("invalid data format"), False),
    ]
    
    for error, expected in test_errors:
        result = handler.is_recoverable_error(error)
        status = "✓" if result == expected else "✗"
        print(f"{status} {type(error).__name__}: {error} - 可恢复: {result}")
    
    print()


def test_retry_decorator():
    """测试重试装饰器"""
    print("=" * 60)
    print("测试 5: 重试装饰器")
    print("=" * 60)
    
    handler = ErrorHandler(log_level="INFO")
    
    # 测试成功的情况
    @handler.retry_on_error(max_retries=3, delay=0.1)
    def successful_function():
        print("  执行成功的函数")
        return "success"
    
    result = successful_function()
    print(f"✓ 成功执行: {result}")
    
    # 测试失败后重试的情况
    attempt_count = [0]
    
    @handler.retry_on_error(max_retries=2, exceptions=(ValueError,), delay=0.1)
    def failing_function():
        attempt_count[0] += 1
        print(f"  尝试 #{attempt_count[0]}")
        if attempt_count[0] < 3:
            raise ValueError("模拟失败")
        return "success after retries"
    
    try:
        result = failing_function()
        print(f"✓ 重试后成功: {result}")
    except ValueError as e:
        print(f"✗ 重试失败: {e}")
    
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("错误场景测试")
    print("=" * 60 + "\n")
    
    try:
        test_basic_exceptions()
        test_error_handler()
        test_api_error_handling()
        test_error_recovery()
        test_retry_decorator()
        
        print("=" * 60)
        print("所有测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
