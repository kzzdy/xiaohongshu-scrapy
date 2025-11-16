"""RateLimiter 单元测试"""

import pytest
import time
import threading
from src.core.rate_limiter import RateLimiter


class TestRateLimiter:
    """测试 RateLimiter 速率限制器"""

    def test_init_default_rate(self):
        """测试默认速率初始化"""
        limiter = RateLimiter()
        
        assert limiter.rate == 3.0
        assert limiter.interval == 1.0 / 3.0
        assert limiter.request_count == 0
        assert limiter.throttle_count == 0

    def test_init_custom_rate(self):
        """测试自定义速率初始化"""
        limiter = RateLimiter(rate=5.0)
        
        assert limiter.rate == 5.0
        assert limiter.interval == 1.0 / 5.0

    def test_init_invalid_rate(self):
        """测试无效速率初始化"""
        with pytest.raises(ValueError) as exc_info:
            RateLimiter(rate=0)
        
        assert "速率必须大于0" in str(exc_info.value)
        
        with pytest.raises(ValueError):
            RateLimiter(rate=-1)

    def test_acquire_single_request(self):
        """测试单个请求"""
        limiter = RateLimiter(rate=10.0)
        
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        
        assert limiter.request_count == 1
        assert limiter.throttle_count == 0
        assert elapsed < 0.1  # 第一个请求应该立即通过

    def test_acquire_rate_limiting(self):
        """测试速率限制功能"""
        limiter = RateLimiter(rate=2.0)  # 每秒2个请求
        
        start = time.time()
        for _ in range(4):
            limiter.acquire()
        elapsed = time.time() - start
        
        # 4个请求应该花费约2秒（第1个立即，第2个等0.5秒，第3个等0.5秒，第4个等0.5秒）
        assert 1.4 < elapsed < 2.2
        assert limiter.request_count == 4
        assert limiter.throttle_count == 3  # 后3个请求被限流

    def test_acquire_high_rate(self):
        """测试高速率请求"""
        limiter = RateLimiter(rate=100.0)  # 每秒100个请求
        
        start = time.time()
        for _ in range(10):
            limiter.acquire()
        elapsed = time.time() - start
        
        # 10个请求应该很快完成
        assert elapsed < 0.2
        assert limiter.request_count == 10

    def test_get_stats(self):
        """测试获取统计信息"""
        limiter = RateLimiter(rate=5.0)
        
        # 初始统计
        stats = limiter.get_stats()
        assert stats["rate"] == 5.0
        assert stats["request_count"] == 0
        assert stats["throttle_count"] == 0
        assert stats["throttle_rate"] == "0.00%"
        
        # 发送一些请求
        for _ in range(5):
            limiter.acquire()
        
        stats = limiter.get_stats()
        assert stats["request_count"] == 5
        assert stats["throttle_count"] >= 0

    def test_reset_stats(self):
        """测试重置统计信息"""
        limiter = RateLimiter(rate=5.0)
        
        # 发送一些请求
        for _ in range(3):
            limiter.acquire()
        
        assert limiter.request_count > 0
        
        # 重置统计
        limiter.reset_stats()
        
        assert limiter.request_count == 0
        assert limiter.throttle_count == 0

    def test_update_rate(self):
        """测试更新速率"""
        limiter = RateLimiter(rate=3.0)
        
        assert limiter.rate == 3.0
        assert limiter.interval == 1.0 / 3.0
        
        # 更新速率
        limiter.update_rate(5.0)
        
        assert limiter.rate == 5.0
        assert limiter.interval == 1.0 / 5.0

    def test_update_rate_invalid(self):
        """测试更新为无效速率"""
        limiter = RateLimiter(rate=3.0)
        
        with pytest.raises(ValueError) as exc_info:
            limiter.update_rate(0)
        
        assert "速率必须大于0" in str(exc_info.value)
        
        # 速率应该保持不变
        assert limiter.rate == 3.0

    def test_thread_safety(self):
        """测试线程安全性"""
        limiter = RateLimiter(rate=10.0)
        results = []
        
        def make_requests():
            for _ in range(5):
                limiter.acquire()
                results.append(time.time())
        
        # 创建多个线程同时请求
        threads = [threading.Thread(target=make_requests) for _ in range(3)]
        
        start = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        elapsed = time.time() - start
        
        # 15个请求，速率10/秒，应该花费约1.5秒
        assert 1.0 < elapsed < 2.0
        assert limiter.request_count == 15
        assert len(results) == 15

    def test_throttle_rate_calculation(self):
        """测试限流率计算"""
        limiter = RateLimiter(rate=2.0)
        
        # 快速发送多个请求，触发限流
        for _ in range(5):
            limiter.acquire()
        
        stats = limiter.get_stats()
        
        # 应该有4个请求被限流（第一个不限流）
        assert stats["request_count"] == 5
        assert stats["throttle_count"] == 4
        assert "80.00%" in stats["throttle_rate"]

    def test_acquire_timing_precision(self):
        """测试请求时间精度"""
        limiter = RateLimiter(rate=1.0)  # 每秒1个请求
        
        times = []
        for _ in range(3):
            start = time.time()
            limiter.acquire()
            times.append(time.time() - start)
        
        # 第一个请求应该立即通过
        assert times[0] < 0.1
        
        # 第二、三个请求应该等待约1秒
        assert 0.9 < times[1] < 1.1
        assert 0.9 < times[2] < 1.1

    def test_concurrent_acquire(self):
        """测试并发获取许可"""
        limiter = RateLimiter(rate=5.0)
        acquired_times = []
        lock = threading.Lock()
        
        def acquire_and_record():
            limiter.acquire()
            with lock:
                acquired_times.append(time.time())
        
        # 同时启动10个线程
        threads = [threading.Thread(target=acquire_and_record) for _ in range(10)]
        
        start = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # 验证所有请求都完成了
        assert len(acquired_times) == 10
        assert limiter.request_count == 10
        
        # 验证请求是按速率限制的
        total_time = time.time() - start
        expected_time = 10 / 5.0  # 10个请求，速率5/秒
        assert total_time >= expected_time * 0.9  # 允许10%误差

    def test_stats_with_no_requests(self):
        """测试无请求时的统计信息"""
        limiter = RateLimiter(rate=3.0)
        
        stats = limiter.get_stats()
        
        assert stats["rate"] == 3.0
        assert stats["request_count"] == 0
        assert stats["throttle_count"] == 0
        assert stats["throttle_rate"] == "0.00%"
