#!/usr/bin/env python3
"""日志清理脚本

手动清理过期的日志文件。虽然loguru已经配置了自动清理，
但此脚本可用于手动清理或在特殊情况下使用。
"""

import argparse
from pathlib import Path
from datetime import datetime, timedelta
import sys


def cleanup_logs(
    log_dir: str = "logs",
    days: int = 30,
    dry_run: bool = False,
    pattern: str = "*.log*"
) -> None:
    """清理过期的日志文件
    
    Args:
        log_dir: 日志目录路径
        days: 保留天数，超过此天数的日志将被删除
        dry_run: 是否为试运行模式（不实际删除文件）
        pattern: 文件匹配模式
    """
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"错误: 日志目录不存在: {log_dir}")
        sys.exit(1)
    
    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=days)
    
    print(f"日志清理工具")
    print(f"=" * 60)
    print(f"日志目录: {log_path.absolute()}")
    print(f"保留天数: {days} 天")
    print(f"截止日期: {cutoff_date.strftime('%Y-%m-%d')}")
    print(f"文件模式: {pattern}")
    print(f"运行模式: {'试运行（不删除文件）' if dry_run else '实际删除'}")
    print(f"=" * 60)
    print()
    
    # 查找所有日志文件
    log_files = list(log_path.glob(pattern))
    
    if not log_files:
        print("未找到日志文件")
        return
    
    deleted_count = 0
    deleted_size = 0
    kept_count = 0
    
    for log_file in sorted(log_files):
        # 跳过 .gitkeep 文件
        if log_file.name == ".gitkeep":
            continue
        
        # 获取文件修改时间
        file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        file_size = log_file.stat().st_size
        
        # 判断是否需要删除
        if file_mtime < cutoff_date:
            size_str = format_size(file_size)
            print(f"[删除] {log_file.name} ({size_str}, {file_mtime.strftime('%Y-%m-%d')})")
            
            if not dry_run:
                try:
                    log_file.unlink()
                    deleted_count += 1
                    deleted_size += file_size
                except Exception as e:
                    print(f"  错误: 无法删除文件 - {e}")
            else:
                deleted_count += 1
                deleted_size += file_size
        else:
            kept_count += 1
            if dry_run:
                size_str = format_size(file_size)
                print(f"[保留] {log_file.name} ({size_str}, {file_mtime.strftime('%Y-%m-%d')})")
    
    print()
    print(f"=" * 60)
    print(f"清理完成")
    print(f"删除文件: {deleted_count} 个")
    print(f"释放空间: {format_size(deleted_size)}")
    print(f"保留文件: {kept_count} 个")
    print(f"=" * 60)


def format_size(size_bytes: int) -> str:
    """格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="清理过期的日志文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 试运行，查看将要删除的文件（不实际删除）
  python scripts/cleanup_logs.py --dry-run
  
  # 删除30天前的日志
  python scripts/cleanup_logs.py --days 30
  
  # 删除7天前的日志
  python scripts/cleanup_logs.py --days 7
  
  # 指定日志目录
  python scripts/cleanup_logs.py --log-dir /path/to/logs --days 30
        """
    )
    
    parser.add_argument(
        "--log-dir",
        default="logs",
        help="日志目录路径（默认: logs）"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="保留天数，超过此天数的日志将被删除（默认: 30）"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，不实际删除文件"
    )
    
    parser.add_argument(
        "--pattern",
        default="*.log*",
        help="文件匹配模式（默认: *.log*）"
    )
    
    args = parser.parse_args()
    
    try:
        cleanup_logs(
            log_dir=args.log_dir,
            days=args.days,
            dry_run=args.dry_run,
            pattern=args.pattern
        )
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
