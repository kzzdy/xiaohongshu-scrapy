# 命令行界面 (CLI)

小红书爬虫的命令行界面，提供友好的交互方式来使用爬虫功能。

## 功能特性

- **搜索功能**: 搜索笔记和用户
- **用户爬取**: 获取用户信息和所有笔记
- **笔记爬取**: 爬取指定笔记，支持批量和断点续传
- **多种导出格式**: 支持 Excel、JSON、CSV
- **媒体下载**: 可选下载图片和视频
- **友好的错误提示**: 清晰的错误信息和使用示例

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

在使用前，需要配置 Cookie：

1. 复制 `.env.example` 为 `.env`
2. 登录小红书网页版
3. 获取 Cookie 并填入 `.env` 文件

## 使用方法

### 基本命令

```bash
# 显示帮助
python -m src.cli.main --help

# 显示子命令帮助
python -m src.cli.main search --help
python -m src.cli.main user --help
python -m src.cli.main note --help
```

### 搜索笔记

```bash
# 基本搜索
python -m src.cli.main search "美食"

# 指定数量和排序
python -m src.cli.main search "旅游" --num 50 --sort time

# 只搜索视频笔记
python -m src.cli.main search "健身" --note-type video

# 导出为 JSON 格式
python -m src.cli.main search "摄影" --format json

# 下载媒体文件
python -m src.cli.main search "美食" --save-media
```

**搜索参数说明：**

- `--type`: 搜索类型 (note/user)，默认 note
- `--num`: 结果数量，默认 20
- `--sort`: 排序方式 (general/time/popularity/comment/collect)
- `--note-type`: 笔记类型 (all/video/normal)
- `--format`: 导出格式 (excel/json/csv)
- `--save-media`: 保存媒体文件
- `--no-export`: 不导出数据文件

### 搜索用户

```bash
# 搜索用户
python -m src.cli.main search "美食博主" --type user --num 10
```

### 爬取用户信息

```bash
# 只获取用户信息
python -m src.cli.main user <user_url>

# 获取用户信息和所有笔记
python -m src.cli.main user <user_url> --fetch-notes

# 限制笔记数量
python -m src.cli.main user <user_url> --fetch-notes --max-notes 50

# 下载媒体文件
python -m src.cli.main user <user_url> --fetch-notes --save-media

# 导出为 CSV 格式
python -m src.cli.main user <user_url> --fetch-notes --format csv
```

**用户参数说明：**

- `url`: 用户主页 URL（必填）
- `--fetch-notes`: 获取用户的所有笔记
- `--max-notes`: 最大笔记数量
- `--format`: 导出格式 (excel/json/csv)
- `--save-media`: 保存媒体文件
- `--no-export`: 不导出数据文件

### 爬取笔记

```bash
# 爬取单个笔记
python -m src.cli.main note <note_url>

# 爬取多个笔记
python -m src.cli.main note <note_url1> <note_url2> <note_url3>

# 下载媒体文件
python -m src.cli.main note <note_url> --save-media

# 启用断点续传
python -m src.cli.main note <note_url1> <note_url2> --resume

# 清除进度记录
python -m src.cli.main note <note_url> --clear-progress

# 导出为 JSON 格式
python -m src.cli.main note <note_url> --format json
```

**笔记参数说明：**

- `url`: 笔记 URL，可以指定多个（必填）
- `--save-media`: 保存媒体文件（图片和视频）
- `--format`: 导出格式 (excel/json/csv)
- `--no-export`: 不导出数据文件
- `--resume`: 启用断点续传（跳过已完成的笔记）
- `--clear-progress`: 清除进度记录

## 全局参数

所有命令都支持以下全局参数：

- `--config`: 配置文件路径，默认 `.env`
- `--log-level`: 日志级别 (DEBUG/INFO/WARNING/ERROR)，默认 INFO

示例：

```bash
# 使用自定义配置文件
python -m src.cli.main search "美食" --config .env.prod

# 设置日志级别为 DEBUG
python -m src.cli.main search "美食" --log-level DEBUG
```

## 输出说明

### 数据文件

导出的数据文件保存在 `datas/` 目录下：

- Excel 格式: `datas/excel_datas/`
- JSON 格式: `datas/`
- CSV 格式: `datas/`

### 媒体文件

下载的媒体文件保存在 `datas/media_datas/` 目录下，按笔记标题和 ID 组织：

```
datas/media_datas/
├── 美食推荐_123456/
│   ├── image_1.jpg
│   ├── image_2.jpg
│   └── note_detail.txt
└── 旅游攻略_789012/
    ├── video.mp4
    └── note_detail.txt
```

### 日志文件

日志文件保存在 `logs/` 目录下：

- 普通日志: `logs/spider_YYYY-MM-DD.log`
- 错误日志: `logs/error_YYYY-MM-DD.log`

## 常见问题

### Cookie 配置错误

如果看到以下错误：

```
配置加载失败: Cookie配置缺失或无效！
```

请按照以下步骤配置 Cookie：

1. 复制 `.env.example` 文件为 `.env`
2. 登录小红书网页版 (https://www.xiaohongshu.com)
3. 打开浏览器开发者工具（F12）
4. 在 Network 标签中找到任意请求，复制 Cookie 值
5. 将 Cookie 值填入 `.env` 文件的 `COOKIES` 配置项

### 速率限制

为了避免被封禁，爬虫默认限制每秒 3 个请求。可以在 `.env` 文件中调整：

```
RATE_LIMIT=3.0
```

### 断点续传

使用 `--resume` 参数可以在中断后继续下载：

```bash
python -m src.cli.main note <url1> <url2> <url3> --resume
```

进度记录保存在 `datas/.progress.json` 文件中。

如果需要重新开始，使用 `--clear-progress` 清除进度：

```bash
python -m src.cli.main note <url> --clear-progress
```

## 高级用法

### 批量处理

可以结合 shell 脚本进行批量处理：

```bash
# 从文件读取 URL 列表
while read url; do
  python -m src.cli.main note "$url" --save-media
done < urls.txt
```

### 自定义配置

创建不同的配置文件用于不同场景：

```bash
# 开发环境
python -m src.cli.main search "测试" --config .env.dev

# 生产环境
python -m src.cli.main search "美食" --config .env.prod
```

## 架构说明

CLI 模块的主要组件：

- `SpiderCLI`: 主类，负责参数解析和命令分发
- `cmd_search()`: 搜索命令处理
- `cmd_user()`: 用户命令处理
- `cmd_note()`: 笔记命令处理

CLI 集成了以下核心模块：

- `ConfigManager`: 配置管理
- `RateLimiter`: 速率限制
- `ErrorHandler`: 错误处理
- `ProgressManager`: 进度管理
- `NoteSpider`: 笔记爬虫
- `UserSpider`: 用户爬虫
- `SearchSpider`: 搜索爬虫

## 相关文档

- [核心模块文档](../core/README.md)
- [API 层文档](../api/README.md)
- [数据层文档](../data/README.md)
- [爬虫层文档](../spider/README.md)
