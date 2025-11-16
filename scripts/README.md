# 脚本工具

本目录包含项目的辅助脚本工具。

## 优化功能演示

`demo_optimizations.py` - 演示Task 9中实现的优化功能

### 功能

演示以下优化功能：
1. 性能监控 - 实时监控系统和进程资源使用
2. 增强的错误处理 - 智能错误诊断和恢复建议
3. 重试装饰器 - 自动重试失败的操作
4. 连接池优化 - 提高并发性能
5. 流式下载 - 优化大文件下载

### 使用方法

```bash
python scripts/demo_optimizations.py
```

## 错误场景测试

`test_error_scenarios.py` - 测试各种错误场景

### 功能

测试以下错误处理功能：
1. 基本异常类
2. 错误处理器
3. API错误处理
4. 错误恢复机制
5. 重试装饰器

### 使用方法

```bash
python scripts/test_error_scenarios.py
```

## 日志清理脚本

`cleanup_logs.py` - 手动清理过期的日志文件

### 功能

- 删除指定天数之前的日志文件
- 支持试运行模式（查看将要删除的文件但不实际删除）
- 显示清理统计信息（删除文件数、释放空间等）
- 自定义日志目录和文件匹配模式

### 使用方法

```bash
# 试运行，查看将要删除的文件（不实际删除）
python scripts/cleanup_logs.py --dry-run

# 删除30天前的日志（默认）
python scripts/cleanup_logs.py

# 删除7天前的日志
python scripts/cleanup_logs.py --days 7

# 指定日志目录
python scripts/cleanup_logs.py --log-dir /path/to/logs --days 30

# 查看帮助信息
python scripts/cleanup_logs.py --help
```

### 参数说明

- `--log-dir`: 日志目录路径（默认: logs）
- `--days`: 保留天数，超过此天数的日志将被删除（默认: 30）
- `--dry-run`: 试运行模式，不实际删除文件
- `--pattern`: 文件匹配模式（默认: *.log*）

### 注意事项

- loguru 已经配置了自动日志轮转和清理（保留30天）
- 此脚本主要用于手动清理或特殊情况下使用
- 建议先使用 `--dry-run` 模式查看将要删除的文件
- 删除的文件无法恢复，请谨慎操作
