"""性能监控模块

提供内存使用监控和性能统计功能
"""

import psutil
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger


@dataclass
class MemoryStats:
    """内存统计信息"""
    
    total: float  # 总内存 (MB)
    available: float  # 可用内存 (MB)
    used: float  # 已使用内存 (MB)
    percent: float  # 使用百分比
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class ProcessStats:
    """进程统计信息"""
    
    memory_mb: float  # 进程内存使用 (MB)
    memory_percent: float  # 进程内存占比
    cpu_percent: float  # CPU使用率
    num_threads: int  # 线程数
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class PerformanceMonitor:
    """性能监控器
    
    监控系统和进程的资源使用情况，提供性能统计和警告。
    """
    
    def __init__(
        self,
        memory_warning_threshold: float = 80.0,
        memory_critical_threshold: float = 90.0,
        enable_logging: bool = True
    ):
        """初始化性能监控器
        
        Args:
            memory_warning_threshold: 内存使用警告阈值（百分比），默认80%
            memory_critical_threshold: 内存使用严重阈值（百分比），默认90%
            enable_logging: 是否启用日志记录，默认True
        """
        self.memory_warning_threshold = memory_warning_threshold
        self.memory_critical_threshold = memory_critical_threshold
        self.enable_logging = enable_logging
        
        # 获取当前进程
        self.process = psutil.Process()
        
        # 统计信息
        self.start_time = time.time()
        self.peak_memory_mb = 0.0
        self.total_requests = 0
        self.failed_requests = 0
        
        if self.enable_logging:
            logger.info("性能监控器已启动")
    
    def get_system_memory(self) -> MemoryStats:
        """获取系统内存统计信息
        
        Returns:
            MemoryStats对象，包含系统内存信息
        """
        mem = psutil.virtual_memory()
        
        stats = MemoryStats(
            total=mem.total / (1024 * 1024),  # 转换为MB
            available=mem.available / (1024 * 1024),
            used=mem.used / (1024 * 1024),
            percent=mem.percent
        )
        
        # 检查内存使用情况并记录警告
        if self.enable_logging:
            if stats.percent >= self.memory_critical_threshold:
                logger.critical(
                    f"系统内存使用严重: {stats.percent:.1f}% "
                    f"(已使用: {stats.used:.1f}MB / 总计: {stats.total:.1f}MB)"
                )
            elif stats.percent >= self.memory_warning_threshold:
                logger.warning(
                    f"系统内存使用较高: {stats.percent:.1f}% "
                    f"(已使用: {stats.used:.1f}MB / 总计: {stats.total:.1f}MB)"
                )
        
        return stats
    
    def get_process_memory(self) -> ProcessStats:
        """获取当前进程的资源使用统计
        
        Returns:
            ProcessStats对象，包含进程资源信息
        """
        # 获取进程内存信息
        mem_info = self.process.memory_info()
        memory_mb = mem_info.rss / (1024 * 1024)  # 转换为MB
        
        # 更新峰值内存
        if memory_mb > self.peak_memory_mb:
            self.peak_memory_mb = memory_mb
        
        # 获取CPU使用率（需要一定时间间隔）
        cpu_percent = self.process.cpu_percent(interval=0.1)
        
        # 获取内存占比
        memory_percent = self.process.memory_percent()
        
        # 获取线程数
        num_threads = self.process.num_threads()
        
        stats = ProcessStats(
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            cpu_percent=cpu_percent,
            num_threads=num_threads
        )
        
        # 检查进程内存使用
        if self.enable_logging and memory_percent >= 10.0:  # 进程占用超过10%系统内存
            logger.warning(
                f"进程内存使用较高: {memory_mb:.1f}MB ({memory_percent:.1f}%)"
            )
        
        return stats
    
    def log_memory_usage(self) -> None:
        """记录当前内存使用情况"""
        system_mem = self.get_system_memory()
        process_mem = self.get_process_memory()
        
        if self.enable_logging:
            logger.info(
                f"内存使用 - 系统: {system_mem.percent:.1f}% "
                f"({system_mem.used:.1f}MB/{system_mem.total:.1f}MB), "
                f"进程: {process_mem.memory_mb:.1f}MB ({process_mem.memory_percent:.1f}%)"
            )
    
    def record_request(self, success: bool = True) -> None:
        """记录请求统计
        
        Args:
            success: 请求是否成功
        """
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取完整的统计信息
        
        Returns:
            包含所有统计信息的字典
        """
        elapsed_time = time.time() - self.start_time
        system_mem = self.get_system_memory()
        process_mem = self.get_process_memory()
        
        return {
            "runtime": {
                "elapsed_seconds": elapsed_time,
                "elapsed_formatted": self._format_time(elapsed_time)
            },
            "system_memory": {
                "total_mb": system_mem.total,
                "used_mb": system_mem.used,
                "available_mb": system_mem.available,
                "percent": system_mem.percent
            },
            "process_memory": {
                "current_mb": process_mem.memory_mb,
                "peak_mb": self.peak_memory_mb,
                "percent": process_mem.memory_percent
            },
            "process_cpu": {
                "percent": process_mem.cpu_percent,
                "num_threads": process_mem.num_threads
            },
            "requests": {
                "total": self.total_requests,
                "failed": self.failed_requests,
                "success_rate": (
                    (self.total_requests - self.failed_requests) / self.total_requests * 100
                    if self.total_requests > 0 else 0
                )
            }
        }
    
    def print_statistics(self) -> None:
        """打印统计信息"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("性能统计报告")
        print("=" * 60)
        print(f"运行时间: {stats['runtime']['elapsed_formatted']}")
        print(f"\n系统内存:")
        print(f"  总计: {stats['system_memory']['total_mb']:.1f} MB")
        print(f"  已使用: {stats['system_memory']['used_mb']:.1f} MB ({stats['system_memory']['percent']:.1f}%)")
        print(f"  可用: {stats['system_memory']['available_mb']:.1f} MB")
        print(f"\n进程资源:")
        print(f"  当前内存: {stats['process_memory']['current_mb']:.1f} MB")
        print(f"  峰值内存: {stats['process_memory']['peak_mb']:.1f} MB")
        print(f"  内存占比: {stats['process_memory']['percent']:.2f}%")
        print(f"  CPU使用率: {stats['process_cpu']['percent']:.1f}%")
        print(f"  线程数: {stats['process_cpu']['num_threads']}")
        print(f"\n请求统计:")
        print(f"  总请求数: {stats['requests']['total']}")
        print(f"  失败请求: {stats['requests']['failed']}")
        print(f"  成功率: {stats['requests']['success_rate']:.1f}%")
        print("=" * 60 + "\n")
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间字符串
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}小时{minutes}分{secs}秒"
        elif minutes > 0:
            return f"{minutes}分{secs}秒"
        else:
            return f"{secs}秒"
    
    def check_memory_health(self) -> bool:
        """检查内存健康状态
        
        Returns:
            True表示内存使用正常，False表示内存使用过高
        """
        system_mem = self.get_system_memory()
        return system_mem.percent < self.memory_critical_threshold
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，打印统计信息"""
        if self.enable_logging:
            self.print_statistics()
