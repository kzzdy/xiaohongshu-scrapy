# 爬虫业务逻辑层

本目录包含小红书爬虫的业务逻辑实现，提供三个主要的爬虫类。

## 模块结构

```
src/spider/
├── __init__.py          # 模块导出
├── note_spider.py       # 笔记爬虫
├── user_spider.py       # 用户爬虫
├── search_spider.py     # 搜索爬虫
└── README.md           # 本文档
```

## 核心类

### 1. NoteSpider (笔记爬虫)

负责爬取小红书笔记信息，支持单个和批量爬取。

**主要功能：**
- 单个笔记爬取
- 批量笔记爬取
- 媒体文件下载（图片、视频）
- 断点续传支持
- 进度管理

**使用示例：**

```python
from src.spider import NoteSpider
from src.api.xhs_pc import XHSPCApi
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from src.data.exporter import ExportFormat

# 创建API客户端
rate_limiter = RateLimiter(rate=3.0)
error_handler = ErrorHandler()
api_client = XHSPCApi(
    cookies_str="your_cookies",
    rate_limiter=rate_limiter,
    error_handler=error_handler,
)

# 创建笔记爬虫
spider = NoteSpider(api_client=api_client)

# 爬取单个笔记
note = spider.crawl_note(
    note_url="https://www.xiaohongshu.com/explore/xxx",
    save_media=True,
    export_format=ExportFormat.EXCEL,
)

# 批量爬取笔记
notes = spider.crawl_notes(
    note_urls=["url1", "url2", "url3"],
    save_media=True,
    export_format=ExportFormat.JSON,
    use_progress=True,  # 启用断点续传
)
```

### 2. UserSpider (用户爬虫)

负责爬取小红书用户信息和用户的笔记。

**主要功能：**
- 用户信息爬取
- 用户所有笔记爬取
- 用户喜欢的笔记爬取
- 用户收藏的笔记爬取
- 数据验证和导出

**使用示例：**

```python
from src.spider import UserSpider, NoteSpider
from src.api.xhs_pc import XHSPCApi
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from src.data.exporter import ExportFormat

# 创建API客户端
rate_limiter = RateLimiter(rate=3.0)
error_handler = ErrorHandler()
api_client = XHSPCApi(
    cookies_str="your_cookies",
    rate_limiter=rate_limiter,
    error_handler=error_handler,
)

# 创建笔记爬虫（用于下载媒体文件）
note_spider = NoteSpider(api_client=api_client)

# 创建用户爬虫
spider = UserSpider(
    api_client=api_client,
    note_spider=note_spider,
)

# 爬取用户信息和笔记
result = spider.crawl_user(
    user_url="https://www.xiaohongshu.com/user/profile/xxx",
    fetch_notes=True,
    max_notes=50,
    save_media=True,
    export_format=ExportFormat.EXCEL,
)

# 批量爬取用户
users = spider.crawl_users(
    user_urls=["url1", "url2", "url3"],
    fetch_notes=True,
    max_notes=20,
    export_format=ExportFormat.JSON,
)
```

### 3. SearchSpider (搜索爬虫)

负责搜索小红书笔记和用户。

**主要功能：**
- 关键词搜索笔记
- 关键词搜索用户
- 多种排序和筛选选项
- 搜索关键词推荐
- 进度管理和数据导出

**排序选项：**
- `SORT_GENERAL` (0): 综合排序
- `SORT_TIME` (1): 最新
- `SORT_POPULARITY` (2): 最多点赞
- `SORT_COMMENT` (3): 最多评论
- `SORT_COLLECT` (4): 最多收藏

**笔记类型：**
- `NOTE_TYPE_ALL` (0): 不限
- `NOTE_TYPE_VIDEO` (1): 视频笔记
- `NOTE_TYPE_NORMAL` (2): 普通笔记

**笔记时间：**
- `NOTE_TIME_ALL` (0): 不限
- `NOTE_TIME_DAY` (1): 一天内
- `NOTE_TIME_WEEK` (2): 一周内
- `NOTE_TIME_HALF_YEAR` (3): 半年内

**使用示例：**

```python
from src.spider import SearchSpider, NoteSpider
from src.api.xhs_pc import XHSPCApi
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from src.data.exporter import ExportFormat

# 创建API客户端
rate_limiter = RateLimiter(rate=3.0)
error_handler = ErrorHandler()
api_client = XHSPCApi(
    cookies_str="your_cookies",
    rate_limiter=rate_limiter,
    error_handler=error_handler,
)

# 创建笔记爬虫（用于下载媒体文件）
note_spider = NoteSpider(api_client=api_client)

# 创建搜索爬虫
spider = SearchSpider(
    api_client=api_client,
    note_spider=note_spider,
)

# 搜索笔记
notes = spider.crawl_search_notes(
    query="美食",
    num=50,
    sort_type=SearchSpider.SORT_POPULARITY,
    note_type=SearchSpider.NOTE_TYPE_ALL,
    note_time=SearchSpider.NOTE_TIME_WEEK,
    save_media=True,
    export_format=ExportFormat.EXCEL,
    use_progress=True,
)

# 搜索用户
users = spider.crawl_search_users(
    query="美食博主",
    num=20,
    export_format=ExportFormat.JSON,
)

# 获取搜索推荐
recommendations = spider.get_search_recommendations("美食")
print(f"推荐关键词: {recommendations}")
```

## 集成使用

三个爬虫可以组合使用，实现复杂的爬取场景：

```python
from src.spider import NoteSpider, UserSpider, SearchSpider
from src.api.xhs_pc import XHSPCApi
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from src.core.progress import ProgressManager
from src.data.processor import DataProcessor
from src.data.exporter import DataExporter, ExportFormat

# 创建共享依赖
rate_limiter = RateLimiter(rate=3.0)
error_handler = ErrorHandler()
api_client = XHSPCApi(
    cookies_str="your_cookies",
    rate_limiter=rate_limiter,
    error_handler=error_handler,
)
progress_manager = ProgressManager()
data_processor = DataProcessor()
data_exporter = DataExporter()

# 创建笔记爬虫
note_spider = NoteSpider(
    api_client=api_client,
    progress_manager=progress_manager,
    data_processor=data_processor,
    data_exporter=data_exporter,
)

# 创建用户爬虫（集成笔记爬虫）
user_spider = UserSpider(
    api_client=api_client,
    data_processor=data_processor,
    data_exporter=data_exporter,
    note_spider=note_spider,
)

# 创建搜索爬虫（集成笔记爬虫）
search_spider = SearchSpider(
    api_client=api_client,
    progress_manager=progress_manager,
    data_processor=data_processor,
    data_exporter=data_exporter,
    note_spider=note_spider,
)

# 场景1: 搜索笔记并下载
notes = search_spider.crawl_search_notes(
    query="旅游攻略",
    num=100,
    save_media=True,
    export_format=ExportFormat.EXCEL,
)

# 场景2: 爬取用户及其所有笔记
result = user_spider.crawl_user(
    user_url="https://www.xiaohongshu.com/user/profile/xxx",
    fetch_notes=True,
    save_media=True,
    export_format=ExportFormat.JSON,
)

# 场景3: 批量爬取指定笔记
note_urls = ["url1", "url2", "url3"]
notes = note_spider.crawl_notes(
    note_urls=note_urls,
    save_media=True,
    export_format=ExportFormat.CSV,
    use_progress=True,
)
```

## 进度管理

所有爬虫都支持进度管理，可以实现断点续传：

```python
# 获取进度统计
stats = spider.get_progress_stats()
print(f"已完成: {stats['total_completed']} 个笔记")

# 清除进度（重新开始）
spider.clear_progress()
```

## 数据导出

支持多种导出格式：

```python
from src.data.exporter import ExportFormat

# Excel格式
notes = spider.crawl_notes(
    note_urls=urls,
    export_format=ExportFormat.EXCEL,
)

# JSON格式
notes = spider.crawl_notes(
    note_urls=urls,
    export_format=ExportFormat.JSON,
)

# CSV格式
notes = spider.crawl_notes(
    note_urls=urls,
    export_format=ExportFormat.CSV,
)
```

## 错误处理

所有爬虫都集成了错误处理机制：

- 自动重试失败的请求
- 详细的错误日志
- 优雅的错误恢复
- 数据验证失败时跳过并记录

## 速率限制

所有爬虫都遵守速率限制，避免被平台封禁：

```python
# 创建速率限制器（每秒3个请求）
rate_limiter = RateLimiter(rate=3.0)

# 速率限制会自动应用到所有API请求
```

## 注意事项

1. **Cookie配置**: 确保提供有效的Cookie字符串
2. **速率限制**: 建议使用默认的3 req/s，避免请求过快
3. **媒体下载**: 下载大量媒体文件时注意磁盘空间
4. **进度管理**: 使用断点续传时，进度文件保存在 `datas/.progress.json`
5. **数据验证**: 验证失败的数据会被跳过并记录警告日志

## 依赖关系

```
SearchSpider
    ├── XHSPCApi (API客户端)
    ├── ProgressManager (进度管理)
    ├── DataProcessor (数据处理)
    ├── DataExporter (数据导出)
    └── NoteSpider (可选，用于下载媒体)

UserSpider
    ├── XHSPCApi (API客户端)
    ├── DataProcessor (数据处理)
    ├── DataExporter (数据导出)
    └── NoteSpider (可选，用于下载媒体)

NoteSpider
    ├── XHSPCApi (API客户端)
    ├── ProgressManager (进度管理)
    ├── DataProcessor (数据处理)
    └── DataExporter (数据导出)
```

## 测试

运行验证脚本测试爬虫实现：

```bash
python verify_spider_layer.py
```

## 相关文档

- [API层文档](../api/README.md)
- [核心模块文档](../core/README.md)
- [数据层文档](../data/README.md)
