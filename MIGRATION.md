# 迁移指南 (Migration Guide)

本文档帮助你从旧版本的 Spider_XHS 迁移到新的模块化架构版本。

## 📋 目录

- [概述](#概述)
- [主要变化](#主要变化)
- [迁移步骤](#迁移步骤)
- [API对照表](#api对照表)
- [常见问题](#常见问题)

## 概述

新版本进行了全面的架构重构，主要改进包括：

- ✅ 模块化设计，代码结构更清晰
- ✅ 环境变量配置管理，更安全
- ✅ 速率限制和错误处理，更稳定
- ✅ 断点续传功能，更高效
- ✅ 多格式导出支持（JSON/CSV/Excel）
- ✅ 命令行界面（CLI），更易用
- ✅ 单元测试覆盖，更可靠

**重要提示**：新版本完全向后兼容，你可以继续使用旧的 `main.py` 和 `apis/` 目录中的代码。

## 主要变化

### 1. 目录结构变化

**旧版本**：
```
Spider_XHS/
├── apis/
│   ├── xhs_pc_apis.py
│   └── xhs_creator_apis.py
├── xhs_utils/
│   ├── common_util.py
│   ├── data_util.py
│   └── ...
└── main.py
```

**新版本**：
```
Spider_XHS/
├── src/                      # 新增：核心源代码
│   ├── core/                # 核心模块
│   ├── api/                 # API接口层
│   ├── data/                # 数据处理层
│   ├── spider/              # 爬虫业务逻辑
│   └── cli/                 # 命令行界面
├── apis/                     # 保留：兼容旧版本
├── xhs_utils/               # 保留：兼容旧版本
└── main.py                  # 保留：兼容旧版本
```

### 2. 配置管理变化

**旧版本**：
```python
# 直接在代码中硬编码
cookies_str = "your_cookies_here"
```

**新版本**：
```bash
# .env 文件
COOKIES='your_cookies_here'
RATE_LIMIT=3.0
TIMEOUT=30
```

### 3. API调用方式变化

详见下方 [API对照表](#api对照表)。

## 迁移步骤

### 步骤 1：安装新依赖

```bash
pip install -r requirements.txt
```

新增的依赖包括：
- `pydantic`: 数据验证
- `python-dotenv`: 环境变量管理
- `loguru`: 日志管理

### 步骤 2：创建配置文件

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
nano .env  # 或使用其他编辑器
```

在 `.env` 文件中填入：
```bash
COOKIES='your_cookies_here'
RATE_LIMIT=3.0
TIMEOUT=30
RETRY_TIMES=3
```

### 步骤 3：选择迁移方式

你有两种选择：

#### 选项 A：继续使用旧代码（零改动）

如果你不想修改现有代码，可以继续使用：

```bash
python main.py
```

旧代码会继续正常工作，但不会享受新功能（速率限制、断点续传等）。

#### 选项 B：迁移到新API（推荐）

逐步将代码迁移到新的模块化API，享受所有新功能。

### 步骤 4：逐步迁移代码

你可以在同一项目中混用新旧API，逐步迁移。

## API对照表

### 配置管理

**旧版本**：
```python
from xhs_utils.common_util import init

cookies_str, base_path = init()
```

**新版本**：
```python
from src.core.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config()
cookies_str = config.cookies
```

### 获取笔记信息

**旧版本**：
```python
from apis.xhs_pc_apis import XHS_Apis

xhs_apis = XHS_Apis()
success, msg, note_info = xhs_apis.get_note_info(note_url, cookies_str, proxies)
```

**新版本**：
```python
from src.api.xhs_pc import XHSPCApi
from src.core.config import ConfigManager

config = ConfigManager().load_config()
api = XHSPCApi(config)
success, msg, note_info = api.get_note_info(note_url)
```

### 爬取笔记

**旧版本**：
```python
from main import Data_Spider

data_spider = Data_Spider()
data_spider.spider_note(note_url, cookies_str, proxies)
```

**新版本**：
```python
from src.spider.note_spider import NoteSpider
from src.core.config import ConfigManager

config = ConfigManager().load_config()
note_spider = NoteSpider(config)
note_info = note_spider.crawl_note(note_url)
```

### 爬取用户所有笔记

**旧版本**：
```python
data_spider.spider_user_all_note(
    user_url, 
    cookies_str, 
    base_path, 
    'all',
    excel_name='user_notes'
)
```

**新版本**：
```python
from src.spider.user_spider import UserSpider

user_spider = UserSpider(config)
user_spider.crawl_user_notes(
    user_url,
    save_format="excel",
    output_name="user_notes"
)
```

### 搜索笔记

**旧版本**：
```python
data_spider.spider_some_search_note(
    query="美食",
    require_num=10,
    cookies_str=cookies_str,
    base_path=base_path,
    save_choice='all',
    sort_type_choice=0
)
```

**新版本**：
```python
from src.spider.search_spider import SearchSpider

search_spider = SearchSpider(config)
search_spider.search_notes(
    query="美食",
    num=10,
    save_format="excel",
    sort_type=0
)
```

### 数据处理

**旧版本**：
```python
from xhs_utils.data_util import handle_note_info, save_to_xlsx

note_info = handle_note_info(raw_data)
save_to_xlsx(note_list, file_path)
```

**新版本**：
```python
from src.data.processor import DataProcessor
from src.data.exporter import DataExporter, ExportFormat

# 处理数据
processor = DataProcessor()
note_info = processor.process_note(raw_data)

# 导出数据
exporter = DataExporter()
exporter.export(note_list, "output.xlsx", format=ExportFormat.EXCEL)
```

### 下载媒体文件

**旧版本**：
```python
from xhs_utils.data_util import download_note

download_note(note_info, base_path['media'], 'all')
```

**新版本**：
```python
from src.spider.note_spider import NoteSpider

note_spider = NoteSpider(config)
note_spider.download_media(note_info, output_dir="datas/media_datas")
```

## 使用新功能

### 1. 使用CLI命令行界面

新版本提供了友好的CLI：

```bash
# 搜索笔记
python -m src.cli.main search "美食" --num 10 --format excel

# 爬取用户笔记
python -m src.cli.main user <user_url> --format json

# 爬取指定笔记
python -m src.cli.main note <note_url> --save-media

# 查看帮助
python -m src.cli.main --help
```

### 2. 使用断点续传

```python
from src.spider.note_spider import NoteSpider

note_spider = NoteSpider(config)
note_spider.crawl_notes_batch(
    note_urls,
    resume=True  # 启用断点续传
)
```

### 3. 使用速率限制

速率限制会自动应用，你可以在 `.env` 文件中配置：

```bash
RATE_LIMIT=3.0  # 每秒3个请求
```

或在代码中自定义：

```python
from src.core.rate_limiter import RateLimiter

limiter = RateLimiter(rate=5.0)  # 每秒5个请求
```

### 4. 使用多格式导出

```python
from src.data.exporter import DataExporter, ExportFormat

exporter = DataExporter()

# 导出为Excel
exporter.export(data, "output.xlsx", format=ExportFormat.EXCEL)

# 导出为JSON
exporter.export(data, "output.json", format=ExportFormat.JSON)

# 导出为CSV
exporter.export(data, "output.csv", format=ExportFormat.CSV)
```

### 5. 使用错误处理

```python
from src.core.error_handler import ErrorHandler
import logging

logger = logging.getLogger(__name__)
error_handler = ErrorHandler(logger)

# 使用重试装饰器
@error_handler.retry_on_error(max_retries=3, delay=1.0)
def fetch_data():
    # 你的代码
    pass
```

## 常见问题

### Q1: 我必须迁移到新版本吗？

**A**: 不必须。新版本完全向后兼容，你可以继续使用旧代码。但建议逐步迁移以享受新功能。

### Q2: 迁移会影响现有功能吗？

**A**: 不会。旧的 `main.py` 和 `apis/` 目录保持不变，现有功能不受影响。

### Q3: 新旧API可以混用吗？

**A**: 可以。你可以在同一项目中同时使用新旧API，逐步迁移。

### Q4: 配置文件必须使用 .env 吗？

**A**: 不必须。你仍然可以在代码中直接配置，但使用 `.env` 更安全，不会将敏感信息提交到Git。

### Q5: 如何处理Cookie过期？

**A**: 
- 旧版本：修改代码中的 `cookies_str`
- 新版本：只需更新 `.env` 文件中的 `COOKIES` 值

### Q6: 新版本的性能如何？

**A**: 新版本通过以下方式提升了性能：
- 连接池复用
- 速率限制避免被封
- 断点续传避免重复下载
- 更好的错误处理和重试机制

### Q7: 如何查看日志？

**A**: 日志文件位于 `logs/` 目录：
- `spider_YYYY-MM-DD.log`: 普通日志
- `error_YYYY-MM-DD.log`: 错误日志

### Q8: 测试如何运行？

**A**: 
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_config.py

# 查看覆盖率
pytest --cov=src
```

### Q9: 遇到问题如何排查？

**A**: 
1. 查看 `logs/error_*.log` 错误日志
2. 检查 `.env` 配置是否正确
3. 确认Cookie是否有效
4. 查看GitHub Issues或提交新Issue

### Q10: 如何贡献代码？

**A**: 
1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

## 获取帮助

如果在迁移过程中遇到问题：

1. 查看 [README.md](README.md) 了解基本使用
2. 查看 [tests/](tests/) 目录中的测试代码作为示例
3. 在 GitHub 上提交 Issue
4. 加入交流群获取帮助

## 总结

新版本提供了更好的架构和更多功能，但完全向后兼容。你可以：

- ✅ 继续使用旧代码（零改动）
- ✅ 逐步迁移到新API（推荐）
- ✅ 在同一项目中混用新旧API

建议优先迁移以下部分：
1. 配置管理（使用 `.env` 文件）
2. 新项目使用新API
3. 逐步重构旧代码

祝迁移顺利！🎉
