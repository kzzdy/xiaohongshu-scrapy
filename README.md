<p align="center">
  <a href="https://github.com/cv-cat/Spider_XHS" target="_blank" align="center" alt="Go to XHS_Spider Website">
    <picture>
      <img width="220" src="https://github.com/user-attachments/assets/b817a5d2-4ca6-49e9-b7b1-efb07a4fb325" alt="Spider_XHS logo">
    </picture>
  </a>
</p>


<div align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3.7%2B-blue" alt="Python 3.7+">
    </a>
    <a href="https://nodejs.org/zh-cn/">
        <img src="https://img.shields.io/badge/nodejs-18%2B-blue" alt="NodeJS 18+">
    </a>
</div>



# Spider_XHS

**✨ 专业的小红书数据采集解决方案，支持笔记爬取，保存格式为excel或者media**

**✨ 小红书全域运营解决方法，AI一键改写笔记（图文，视频）直接上传**

## ⭐功能列表

**⚠️ 任何涉及数据注入的操作都是不被允许的，本项目仅供学习交流使用，如有违反，后果自负**

| 模块           | 已实现                                                                             |
|---------------|---------------------------------------------------------------------------------|
| 小红书创作者平台 | ✅ 二维码登录<br/>✅ 手机验证码登录<br/>✅ 上传（图集、视频）作品<br/>✅查看自己上传的作品      |
|    小红书PC    | ✅ 二维码登录<br/> ✅ 手机验证码登录<br/> ✅ 获取无水印图片<br/> ✅ 获取无水印视频<br/> ✅ 获取主页的所有频道<br/>✅ 获取主页推荐笔记<br/>✅ 获取某个用户的信息<br/>✅ 用户自己的信息<br/>✅ 获取某个用户上传的笔记<br/>✅ 获取某个用户所有的喜欢笔记<br/>✅ 获取某个用户所有的收藏笔记<br/>✅ 获取某个笔记的详细内容<br/>✅ 搜索笔记内容<br/>✅ 搜索用户内容<br/>✅ 获取某个笔记的评论<br/>✅ 获取未读消息信息<br/>✅ 获取收到的评论和@提醒信息<br/>✅ 获取收到的点赞和收藏信息<br/>✅ 获取新增关注信息|


## 🌟 功能特性

- ✅ **多维度数据采集**
  - 用户主页信息
  - 笔记详细内容
  - 智能搜索结果抓取
- 🚀 **高性能架构**
  - 自动重试机制
  - 速率限制保护（可配置）
  - 连接池复用
  - 断点续传支持
- 🔒 **安全稳定**
  - 小红书最新API适配
  - 完善的异常处理机制
- 🎨 **多种使用方式**
  - 图形界面（GUI）- 无需编程，开箱即用
  - 命令行（CLI）- 适合自动化脚本
  - Python API - 灵活集成到你的项目
  - 环境变量配置管理
  - proxy代理支持
- 🎨 **便捷管理**
  - 结构化目录存储
  - 多格式输出（JSON/CSV/EXCEL/MEDIA）
  - 命令行界面（CLI）
  - 进度跟踪和恢复
- 🧪 **代码质量**
  - 模块化架构设计
  - 类型注解支持
  - 单元测试覆盖
  - 完善的日志系统
  
## 🎨效果图
### 处理后的所有用户
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/00902dbd-4da1-45bc-90bb-19f5856a04ad)
### 某个用户所有的笔记
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/880884e8-4a1d-4dc1-a4dc-e168dd0e9896)
### 某个笔记具体的内容
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/d17f3f4e-cd44-4d3a-b9f6-d880da626cc8)
### 保存的excel
![image](https://github.com/user-attachments/assets/707f20ed-be27-4482-89b3-a5863bc360e7)

## 🛠️ 快速开始
### ⛳运行环境
- Python 3.7+
- Node.js 18+

### 🎯安装依赖
```
pip install -r requirements.txt
npm install
```

### 🎨配置文件

#### 方式一：使用环境变量（推荐）

1. 复制 `.env.example` 文件为 `.env`：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的配置：
```bash
# 必填：小红书Cookie
COOKIES='your_cookies_here'

# 可选：速率限制（每秒请求数）
RATE_LIMIT=3.0

# 可选：请求超时时间（秒）
TIMEOUT=30

# 可选：重试次数
RETRY_TIMES=3
```

3. **获取Cookie方法**：
   - 登录小红书网页版
   - 按 F12 打开浏览器开发者工具
   - 点击"网络"（Network）标签
   - 点击"Fetch/XHR"筛选
   - 刷新页面，找到任意请求
   - 在请求头中复制完整的 Cookie 值

![image](https://github.com/user-attachments/assets/6a7e4ecb-0432-4581-890a-577e0eae463d)

复制cookie到.env文件中（注意！登录小红书后的cookie才是有效的，不登陆没有用）
![image](https://github.com/user-attachments/assets/5e62bc35-d758-463e-817c-7dcaacbee13c)

#### 方式二：直接在代码中配置（兼容旧版本）

仍然支持在 `main.py` 中直接配置，详见下方运行项目部分。

### 🚀运行项目

#### 方式一：使用图形界面（GUI）- 最简单 ⭐

**适合不熟悉命令行的用户，提供友好的图形界面操作。**

1. **启动GUI**：
   ```bash
   python gui_main.py
   ```
   
   或者在Windows下直接双击 `启动GUI.bat` 文件

2. **使用步骤**：
   - 在"配置"页面加载配置（自动从.env读取）
   - 选择功能页面（笔记爬取/用户爬取/搜索爬取）
   - 输入相应的URL或关键词
   - 选择保存格式和选项
   - 点击"开始爬取"按钮
   - 在"日志"页面查看实时进度

3. **GUI功能**：
   - ⚙️ 配置管理 - 可视化配置Cookie和参数
   - 🔍 搜索爬取 - 搜索关键词，保存笔记列表为JSON
   - 📁 JSON管理器 - 查看和提取笔记链接
   - 📝 笔记爬取 - 批量下载完整笔记内容（图片/视频）
   - 📋 实时日志 - 查看运行状态和错误信息

**推荐工作流程**：
```
第一步：搜索爬取 → 获取笔记列表（JSON）
第二步：JSON管理器 → 提取笔记链接
第三步：笔记爬取 → 下载完整内容（图片/视频）
```

详细使用说明请查看：[GUI使用指南](src/gui/README.md)

#### 方式二：使用命令行（CLI）

新版本提供了更友好的命令行界面：

```bash
# 搜索笔记并保存
python -m src.cli.main search "美食" --num 10 --format excel

# 爬取用户所有笔记
python -m src.cli.main user <user_url> --format json

# 爬取指定笔记
python -m src.cli.main note <note_url> --save-media

# 查看帮助
python -m src.cli.main --help
```

**CLI参数说明**：
- `--num`: 搜索数量
- `--format`: 输出格式（excel/json/csv）
- `--save-media`: 是否下载媒体文件
- `--resume`: 启用断点续传
- `--sort`: 排序方式（综合/最新/最多点赞等）

#### 方式二：使用传统方式（兼容旧版本）

```bash
python main.py
```

编辑 `main.py` 文件，根据需求选择功能：
```python
# 1. 爬取指定笔记列表
notes = ['note_url_1', 'note_url_2']
data_spider.spider_some_note(notes, cookies_str, base_path, 'all', 'test')

# 2. 爬取用户所有笔记
user_url = 'user_profile_url'
data_spider.spider_user_all_note(user_url, cookies_str, base_path, 'all')

# 3. 搜索关键词
data_spider.spider_some_search_note("关键词", 10, cookies_str, base_path, 'all')
```

### 🗝️注意事项
- **新版架构**：项目已重构为模块化架构，核心代码位于 `src/` 目录
  - `src/core/`: 核心模块（配置、限流、错误处理、进度管理）
  - `src/api/`: API接口层
  - `src/data/`: 数据处理层（验证、处理、导出）
  - `src/spider/`: 爬虫业务逻辑
  - `src/cli/`: 命令行界面
- **兼容性**：保留了 `main.py` 和 `apis/` 目录以兼容旧版本代码
- **配置管理**：推荐使用 `.env` 文件管理配置，更安全便捷
- **测试**：运行 `pytest` 执行单元测试


## 📚 使用示例

### 基础示例

```python
from src.spider.note_spider import NoteSpider
from src.spider.user_spider import UserSpider
from src.spider.search_spider import SearchSpider
from src.core.config import ConfigManager

# 加载配置
config_manager = ConfigManager()
config = config_manager.load_config()

# 1. 爬取单个笔记
note_spider = NoteSpider(config)
note_info = note_spider.crawl_note("note_url")

# 2. 爬取用户笔记
user_spider = UserSpider(config)
user_spider.crawl_user_notes("user_url", save_format="excel")

# 3. 搜索笔记
search_spider = SearchSpider(config)
search_spider.search_notes("关键词", num=20, save_format="json")
```

### 高级功能

```python
# 断点续传
note_spider.crawl_notes_batch(note_urls, resume=True)

# 自定义导出格式
from src.data.exporter import DataExporter, ExportFormat

exporter = DataExporter()
exporter.export(data, "output.csv", format=ExportFormat.CSV)

# 速率限制配置
from src.core.rate_limiter import RateLimiter

limiter = RateLimiter(rate=5.0)  # 每秒5个请求
```

### 最佳实践

1. **使用环境变量管理敏感信息**
   - 不要将 Cookie 硬编码在代码中
   - 使用 `.env` 文件，并确保它在 `.gitignore` 中

2. **合理设置速率限制**
   - 默认 3 req/s 较为安全
   - 过快可能导致账号被限制

3. **启用断点续传**
   - 大批量爬取时建议启用
   - 避免重复下载已完成的内容

4. **日志监控**
   - 查看 `logs/` 目录下的日志文件
   - 错误日志单独记录便于排查

## 🔄 迁移指南

### 从旧版本迁移到新版本

如果你正在使用旧版本的代码，可以按以下步骤迁移：

#### 1. 配置迁移

**旧版本**：
```python
cookies_str = "your_cookies"
```

**新版本**：
```bash
# .env 文件
COOKIES='your_cookies'
```

#### 2. API调用迁移

**旧版本**：
```python
from apis.xhs_pc_apis import XHS_Apis

xhs_apis = XHS_Apis()
success, msg, data = xhs_apis.get_note_info(url, cookies)
```

**新版本**：
```python
from src.api.xhs_pc import XHSPCApi
from src.core.config import ConfigManager

config = ConfigManager().load_config()
api = XHSPCApi(config)
success, msg, data = api.get_note_info(url)
```

#### 3. 数据处理迁移

**旧版本**：
```python
from xhs_utils.data_util import handle_note_info, save_to_xlsx

note_info = handle_note_info(raw_data)
save_to_xlsx(notes, "output.xlsx")
```

**新版本**：
```python
from src.data.processor import DataProcessor
from src.data.exporter import DataExporter, ExportFormat

processor = DataProcessor()
note_info = processor.process_note(raw_data)

exporter = DataExporter()
exporter.export(notes, "output.xlsx", format=ExportFormat.EXCEL)
```

#### 4. 兼容性说明

- ✅ **完全兼容**：`main.py` 和 `apis/` 目录保持不变，旧代码可以继续运行
- ⚠️ **建议迁移**：新版本提供更好的错误处理、速率限制和数据验证
- 📝 **逐步迁移**：可以在同一项目中混用新旧API，逐步迁移

## 🍥日志
   
| 日期       | 说明                                        |
|----------|-------------------------------------------|
| 23/08/09 | - 首次提交                                    |
| 23/09/13 | - api更改params增加两个字段，修复图片无法下载，有些页面无法访问导致报错 |
| 23/09/16 | - 较大视频出现编码问题，修复视频编码问题，加入异常处理              |
| 23/09/18 | - 代码重构，加入失败重试                             |
| 23/09/19 | - 新增下载搜索结果功能                              |
| 23/10/05 | - 新增跳过已下载功能，获取更详细的笔记和用户信息                 |
| 23/10/08 | - 上传代码☞Pypi，可通过pip install安装本项目           |
| 23/10/17 | - 搜索下载新增排序方式选项（1、综合排序 2、热门排序 3、最新排序）      |
| 23/10/21 | - 新增图形化界面,上传至release v2.1.0               |
| 23/10/28 | - Fix Bug 修复搜索功能出现的隐藏问题                   |
| 25/03/18 | - 更新API，修复部分问题                            |
| 25/06/07 | - 更新search接口，区分视频和图集下载，增加小红书创作者api        |
| 25/07/15 | - 更新 xs version56 & 小红书创作者接口              |
| 25/11/12 | - 🎉 重大更新：模块化架构重构<br/>- 新增CLI命令行界面<br/>- 新增速率限制和错误处理<br/>- 新增断点续传功能<br/>- 新增多格式导出（JSON/CSV/Excel）<br/>- 新增单元测试<br/>- 改进配置管理（环境变量）<br/>- 完善日志系统<br/>- 保持向后兼容 |


## 🧸额外说明
1. 感谢star⭐和follow📰！不时更新
2. 作者的联系方式在主页里，有问题可以随时联系我
3. 可以关注下作者的其他项目，欢迎 PR 和 issue
4. 感谢赞助！如果此项目对您有帮助，请作者喝一杯奶茶~~ （开心一整天😊😊）
5. thank you~~~

<div align="center">
  <img src="./author/wx_pay.png" width="400px" alt="微信赞赏码"> 
  <img src="./author/zfb_pay.jpg" width="400px" alt="支付宝收款码">
</div>


## 📈 Star 趋势
<a href="https://www.star-history.com/#cv-cat/Spider_XHS&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date" />
 </picture>
</a>

## 🍔 交流群
<img width="1031" height="1449" alt="5355a0f82398ee2052f2e659328d737b" src="https://github.com/user-attachments/assets/ea690f33-0c5f-4941-9332-de9feff838e7" />


