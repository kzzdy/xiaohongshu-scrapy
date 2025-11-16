"""速率限制器模块"""

import time
from threading import Lock
from typing import Dict, Any


class RateLimiter:
    """速率限制器 - 使用令牌桶算法

    控制API请求频率，避免因请求过快被平台封禁。
    使用令牌桶算法实现平滑限流，支持线程安全的并发请求。
    """

    def __init__(self, rate: float = 3.0):
        """初始化速率限制器

        Args:
            rate: 每秒允许的请求数，默认3.0
        """
        if rate <= 0:
            raise ValueError(f"速率必须大于0，当前值: {rate}")

        self.rate = rate
        self.interval = 1.0 / rate  # 两次请求之间的最小间隔
        self.last_request_time = 0.0
        self.lock = Lock()
        self.request_count = 0
        self.throttle_count = 0  # 限流触发次数

    def acquire(self) -> None:
        """获取请求许可，如果超过速率则等待

        此方法会阻塞直到可以发送请求。
        使用令牌桶算法确保请求速率不超过设定值。
        """
        with self.lock:
            current_time = time.time()

            # 计算距离上次请求的时间间隔
            time_since_last_request = current_time - self.last_request_time

            # 如果间隔小于最小间隔，需要等待
            if time_since_last_request < self.interval:
                wait_time = self.interval - time_since_last_request
                self.throttle_count += 1
                time.sleep(wait_time)
                current_time = time.time()

            # 更新最后请求时间和计数
            self.last_request_time = current_time
            self.request_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            包含统计信息的字典，包括：
            - rate: 配置的速率（请求/秒）
            - request_count: 总请求次数
            - throttle_count: 限流触发次数
            - throttle_rate: 限流触发率
        """
        with self.lock:
            throttle_rate = (
                self.throttle_count / self.request_count * 100 if self.request_count > 0 else 0.0
            )

            return {
                "rate": self.rate,
                "request_count": self.request_count,
                "throttle_count": self.throttle_count,
                "throttle_rate": f"{throttle_rate:.2f}%",
            }

    def reset_stats(self) -> None:
        """重置统计信息"""
        with self.lock:
            self.request_count = 0
            self.throttle_count = 0

    def update_rate(self, new_rate: float) -> None:
        """更新速率限制

        Args:
            new_rate: 新的速率（请求/秒）

        Raises:
            ValueError: 如果速率小于等于0
        """
        if new_rate <= 0:
            raise ValueError(f"速率必须大于0，当前值: {new_rate}")

        with self.lock:
            self.rate = new_rate
            self.interval = 1.0 / new_rate
