#!/usr/bin/env python3
"""优化功能演示脚本

演示Task 9中实现的性能优化、日志管理和错误处理功能。
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import PerformanceMonitor, ErrorHandler, RateLimiter
from src.core.error_handler import NetworkError, RateLimitError


def demo_performance_monitor():
    """演示性能监控功能"""
    print("\n" + "=" * 60)
    print("演示 1: 性能监控")
    print("=" * 60 + "\n")
    
    with PerformanceMonitor(enable_logging=True) as monitor:
        print("开始模拟任务...")
        
        # 模拟一些工作
        for i in range(5):
            time.sleep(0.2)
            monitor.record_request(success=True)
            
            if i == 2:
                # 记录一次内存使用
                monitor.log_memory_usage()
        
        # 模拟一次失败
        monitor.record_request(success=False)
        
        print("\n任务完成，查看统计信息...")
    
    # 退出上下文管理器时会自动打印统计报告


def demo_error_handling():
    """演示错误处理功能"""
    print("\n" + "=" * 60)
    print("演示 2: 增强的错误处理")
    print("=" * 60 + "\n")
    
    handler = ErrorHandler(log_level="INFO")
    
    # 模拟不同类型的错误
    print("1. 模拟网络超时错误:")
    error = NetworkError("Connection timeout", {"timeout": 30})
    print(f"   错误: {error}")
    print(f"   可恢复: {handler.is_recoverable_error(error)}")
    
    print("\n2. 模拟速率限制错误:")
    error = RateLimitError("Too many requests", {"limit": "3/s"})
    print(f"   错误: {error}")
    print(f"   可恢复: {handler.is_recoverable_error(error)}")
    
    print("\n3. 模拟API错误并获取恢复建议:")
    # 创建模拟响应对象
    mock_response = type('obj', (object,), {
        'status_code': 429,
        'text': '{"error": "Rate limit exceeded"}'
    })()
    
    error_info = handler.handle_api_error(
        Exception("Too many requests"),
        "https://api.example.com/data",
        mock_response
    )
    
    print(f"   可恢复: {error_info['recoverable']}")
    print(f"   建议: {error_info['suggestion']}")
    
    recovery_action = handler.suggest_recovery_action(error_info)
    print(f"   恢复操作: {recovery_action}")


def demo_retry_decorator():
    """演示重试装饰器"""
    print("\n" + "=" * 60)
    print("演示 3: 重试装饰器")
    print("=" * 60 + "\n")
    
    handler = ErrorHandler(log_level="INFO")
    
    # 模拟一个会失败几次然后成功的函数
    attempt_count = [0]
    
    @handler.retry_on_error(max_retries=3, exceptions=(ValueError,), delay=0.5)
    def unstable_function():
        attempt_count[0] += 1
        print(f"尝试 #{attempt_count[0]}")
        
        if attempt_count[0] < 3:
            raise ValueError("模拟临时失败")
        
        return "成功!"
    
    try:
        result = unstable_function()
        print(f"\n最终结果: {result}")
    except ValueError as e:
        print(f"\n失败: {e}")


def demo_connection_pool():
    """演示连接池优化"""
    print("\n" + "=" * 60)
    print("演示 4: 连接池优化")
    print("=" * 60 + "\n")
    
    from src.api.base import BaseAPIClient
    
    # 创建API客户端
    rate_limiter = RateLimiter(rate=5.0)
    error_handler = ErrorHandler(log_level="INFO")
    
    client = BaseAPIClient(
        base_url="https://httpbin.org",
        rate_limiter=rate_limiter,
        error_handler=error_handler,
        timeout=10
    )
    
    print("连接池配置:")
    print(f"  pool_connections: 20")
    print(f"  pool_maxsize: 50")
    print(f"  pool_block: False")
    print("\n这些优化可以:")
    print("  - 支持更多并发连接")
    print("  - 复用TCP连接，减少握手开销")
    print("  - 避免连接池满时的阻塞")
    
    client.close()


def demo_streaming_download():
    """演示流式下载"""
    print("\n" + "=" * 60)
    print("演示 5: 流式下载")
    print("=" * 60 + "\n")
    
    print("流式下载特性:")
    print("  - 使用 stream=True 参数")
    print("  - 分块读取文件 (默认8KB)")
    print("  - 避免大文件占用内存")
    print("  - 自动创建目录结构")
    print("  - 显示下载文件大小")
    print("\n使用示例:")
    print("  success, msg = client.download_file(")
    print("      url='https://example.com/large_file.mp4',")
    print("      filepath='downloads/video.mp4',")
    print("      chunk_size=8192")
    print("  )")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Task 9 优化功能演示")
    print("=" * 60)
    
    try:
        demo_performance_monitor()
        demo_error_handling()
        demo_retry_decorator()
        demo_connection_pool()
        demo_streaming_download()
        
        print("\n" + "=" * 60)
        print("演示完成!")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n演示已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
