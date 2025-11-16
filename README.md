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
    <a href="https://github.com/cv-cat/Spider_XHS/releases">
        <img src="https://img.shields.io/badge/version-2.2.0-green" alt="Version 2.2.0">
    </a>
</div>

# Spider_XHS

**✨ 专业的小红书数据采集解决方案 - 提供友好的GUI图形界面**

**🎨 无需编程，开箱即用 | 三步式工作流程 | 智能反爬虫策略**

## ⚠️ 免责声明

**本项目仅供学习交流使用，请勿用于商业用途或非法用途。使用本项目所产生的一切后果由使用者自行承担，与开发者无关。**

## 🎯 核心特性

### 🖥️ 友好的GUI界面
- **零编程基础** - 图形化操作，无需编写代码
- **三步式工作流程** - 搜索 → JSON管理器 → 笔记爬取
- **实时进度显示** - 可视化爬取进度和日志
- **智能反爬虫** - 分步操作，降低被检测风险

### 📊 强大的数据采集
- **搜索爬取** - 根据关键词搜索笔记，支持多种排序方式
- **笔记详情** - 获取笔记完整信息（标题、内容、作者、互动数据）
- **媒体下载** - 自动下载高清图片和视频
- **批量处理** - 支持批量爬取多个笔记

### 💾 灵活的数据导出
- **多种格式** - Excel、JSON、CSV任意选择
- **结构化存储** - 自动分类整理数据和媒体文件
- **JSON管理器** - 可视化管理搜索结果，提取笔记链接


## 🌟 技术特性

- 🏗️ **模块化架构**
  - 清晰的代码结构，易于维护和扩展
  - 核心模块：配置管理、速率限制、错误处理、进度跟踪
  
- 🛡️ **安全稳定**
  - 智能速率限制，避免触发反爬虫
  - 完善的错误处理和自动重试机制
  - 断点续传，支持中断后继续
  
- 🎨 **多种使用方式**
  - **GUI图形界面** - 推荐，无需编程基础
  - **CLI命令行** - 适合自动化脚本
  - **Python API** - 灵活集成到你的项目
  
- 📝 **完善的文档**
  - 详细的使用教程
  - 快速开始指南
  - API文档和示例代码
  
## 🎨 GUI界面预览

### 配置页面
![配置页面](https://github.com/cv-cat/Spider_XHS/assets/94289429/config-page.png)

### 搜索爬取页面
![搜索页面](https://github.com/cv-cat/Spider_XHS/assets/94289429/search-page.png)

### JSON管理器页面
![JSON管理器](https://github.com/cv-cat/Spider_XHS/assets/94289429/json-manager.png)

### 笔记爬取页面
![笔记爬取](https://github.com/cv-cat/Spider_XHS/assets/94289429/note-crawler.png)

### 导出的Excel文件
![Excel文件](https://github.com/user-attachments/assets/707f20ed-be27-4482-89b3-a5863bc360e7)

## 🚀 快速开始

### 📋 环境要求
- Python 3.7+
- Node.js 18+（用于签名算法）

### 📦 安装步骤

#### 1. 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖
npm install
```

#### 2. 配置Cookie

**在GUI中配置（最简单）：**

1. 启动GUI：`python gui_main.py` 或双击 `启动GUI.bat`
2. 在"配置"标签页点击"创建示例.env"
3. 点击"打开.env文件"
4. 将你的Cookie粘贴到 `COOKIES=` 后面
5. 保存文件并点击"重新加载配置"

**手动创建.env文件：**

```bash
# 复制配置模板
cp .env.example .env
```

在 `.env` 文件中填入：
```env
# 必填：小红书Cookie
COOKIES='your_cookies_here'

# 可选：速率限制（每秒请求数，建议1-3）
RATE_LIMIT=1.0

# 可选：请求超时时间（秒）
TIMEOUT=30

# 可选：重试次数
RETRY_TIMES=3
```

#### 3. 获取Cookie

1. 打开小红书网页版：https://www.xiaohongshu.com
2. 登录你的账号
3. 按 `F12` 打开开发者工具
4. 点击 `Network`（网络）标签
5. 点击 `Fetch/XHR` 筛选
6. 刷新页面（按 `F5`）
7. 点击任意一个请求
8. 在右侧找到 `Request Headers`
9. 找到 `Cookie:` 字段
10. 复制整个Cookie值

![获取Cookie](https://github.com/user-attachments/assets/6a7e4ecb-0432-4581-890a-577e0eae463d)

**⚠️ 注意**：Cookie必须在登录状态下获取，未登录的Cookie无效！

![复制Cookie](https://github.com/user-attachments/assets/5e62bc35-d758-463e-817c-7dcaacbee13c)

### 🎮 使用GUI（推荐）⭐

#### 启动方式

**Windows用户（最简单）：**
```
双击 "启动GUI.bat" 文件
```

**所有平台：**
```bash
python gui_main.py
```

#### 三步式工作流程

```
┌─────────────────────────────────────────────────────────────┐
│ 第一步：搜索爬取（获取笔记列表）                              │
├─────────────────────────────────────────────────────────────┤
│ • 输入关键词（如：重庆美食、旅游攻略）                        │
│ • 设置数量（建议10-50，避免触发风控）                        │
│ • 选择排序方式（综合/最新/最热）                             │
│ • 点击"开始搜索（仅保存JSON）"                               │
│ ↓                                                           │
│ 保存到：datas/json_datas/search_关键词_时间.json             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 第二步：JSON管理器（提取笔记链接）                            │
├─────────────────────────────────────────────────────────────┤
│ • 点击"刷新列表"加载JSON文件                                 │
│ • 选择要处理的JSON文件                                       │
│ • 查看笔记列表（标题+链接）                                  │
│ • 点击"复制所有链接"                                         │
│ ↓                                                           │
│ 链接已复制到剪贴板                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 第三步：笔记爬取（下载完整内容）                              │
├─────────────────────────────────────────────────────────────┤
│ • 粘贴链接（Ctrl+V，每行一个）                               │
│ • 选择保存格式（Excel/JSON/CSV）                             │
│ • 勾选"下载图片/视频"                                        │
│ • 点击"开始爬取"                                             │
│ ↓                                                           │
│ 保存到：datas/excel_datas/ 和 datas/media_datas/            │
└─────────────────────────────────────────────────────────────┘
```

#### 为什么要分三步？

✅ **避免触发风控** - 搜索时不下载媒体，请求更轻量  
✅ **灵活筛选** - 可以先搜索多个关键词，再统一处理  
✅ **可恢复性** - JSON文件持久化保存，中断后可继续  
✅ **清晰流程** - 每个步骤职责明确，不会混乱  

#### 详细教程

- [GUI使用说明](GUI使用说明.md) - 完整的使用教程
- [快速开始-GUI](快速开始-GUI.md) - 一分钟上手指南

### 💻 使用CLI（适合开发者）

命令行界面适合自动化脚本和批量处理：

```bash
# 搜索笔记
python -m src.cli.main search "美食" --num 10 --format excel

# 爬取指定笔记
python -m src.cli.main note <note_url> --save-media

# 查看帮助
python -m src.cli.main --help
```

### 🐍 使用Python API（适合集成）

```python
from src.spider.note_spider import NoteSpider
from src.spider.search_spider import SearchSpider
from src.core.config import ConfigManager

# 加载配置
config = ConfigManager().load_config()

# 搜索笔记
search_spider = SearchSpider(config)
search_spider.search_notes("美食", num=20, save_format="excel")

# 爬取单个笔记
note_spider = NoteSpider(config)
note_info = note_spider.crawl_note("note_url")
```

详细API文档请查看：[开发者文档](src/README.md)


## 📁 输出文件结构

所有数据保存在 `datas` 目录：

```
datas/
├── json_datas/              # 搜索结果（JSON格式）
│   └── search_关键词_时间.json
│
├── excel_datas/             # 笔记详情（Excel格式）
│   └── notes_时间.xlsx
│
├── csv_datas/               # 笔记详情（CSV格式）
│   └── notes_时间.csv
│
└── media_datas/             # 媒体文件（图片/视频）
    └── 笔记标题_笔记ID/
        ├── detail.txt       # 笔记详情
        ├── image_1.jpg      # 图片文件
        ├── image_2.jpg
        └── video_1.mp4      # 视频文件
```

## 💡 使用技巧

### 1. 如何提高爬取效率？

- **分批处理**：不要一次爬取太多，建议每次10-50个
- **合理延迟**：在.env中设置 `RATE_LIMIT=1.0`（每秒1个请求）
- **避开高峰**：在非高峰时段使用，减少被限制的风险

### 2. 如何避免被封号？

- **使用三步流程**：搜索时不下载媒体，降低请求频率
- **控制数量**：每次搜索不超过50个笔记
- **适当间隔**：操作之间适当休息，不要连续运行
- **更新Cookie**：Cookie过期后及时更新

### 3. 如何批量处理？

1. 先搜索多个关键词，保存多个JSON文件
2. 在JSON管理器中逐个查看和筛选
3. 最后批量爬取需要的笔记

### 4. 遇到问题怎么办？

1. 查看"日志"标签页的错误信息
2. 检查Cookie是否有效（重新获取）
3. 降低速率限制（增大RATE_LIMIT的值）
4. 查看 [常见问题](GUI使用说明.md#常见问题)
5. 在GitHub上提交Issue

## 📖 文档导航

- **[快速开始](QUICK_START.md)** - 5分钟快速上手
- **[GUI使用说明](GUI使用说明.md)** - 详细的GUI使用教程
- **[快速开始-GUI](快速开始-GUI.md)** - GUI一分钟上手
- **[迁移指南](MIGRATION.md)** - 从旧版本迁移
- **[更新日志](CHANGELOG.md)** - 版本更新记录
- **[项目结构](PROJECT_STRUCTURE.md)** - 代码结构说明

## 🔧 高级功能

### 断点续传

在.env中启用：
```env
ENABLE_RESUME=true
```

程序会记录已下载的笔记，重新运行时自动跳过。

### 速率限制

控制请求频率，避免被限制：
```env
RATE_LIMIT=1.0  # 每秒1个请求（推荐）
```

### 代理支持

在.env中配置代理：
```env
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 批量处理

支持批量输入笔记URL，每行一个：
```
https://www.xiaohongshu.com/explore/note_id_1
https://www.xiaohongshu.com/explore/note_id_2
https://www.xiaohongshu.com/explore/note_id_3
```

## 📝 常见问题

### Q: 提示"配置加载失败"？
**A**: 检查Cookie是否正确填写，是否已过期。Cookie必须在登录状态下获取。

### Q: 爬取失败或没有数据？
**A**: 
1. 检查Cookie是否有效（重新获取）
2. 检查网络连接
3. 降低速率限制（增大RATE_LIMIT的值）
4. 查看日志页面的错误详情

### Q: 如何提高爬取速度？
**A**: 在.env中适当提高速率限制，但不要太高：
```env
RATE_LIMIT=2.0  # 每秒2个请求
```

### Q: Cookie多久会过期？
**A**: Cookie的有效期不固定，通常几天到几周。过期后需要重新获取。

### Q: 可以同时运行多个实例吗？
**A**: 不建议。同时运行多个实例可能触发风控，导致账号被限制。

### Q: 支持哪些数据格式？
**A**: 支持Excel（.xlsx）、JSON（.json）、CSV（.csv）三种格式。

更多问题请查看：[GUI使用说明 - 常见问题](GUI使用说明.md#常见问题)

## 🔄 版本历史

### v2.2.0 (2024-11-16) - 当前版本
- 🎉 GUI工作流程优化
- 📁 新增JSON管理器功能
- 🔄 三步式工作流程
- 📖 完善文档

### v2.1.0 (2024-11-12)
- 🏗️ 模块化架构重构
- 💻 新增CLI命令行界面
- 🛡️ 速率限制和错误处理
- 💾 断点续传功能

### v2.0.0 (2023-10-21)
- 🎨 新增图形化界面

查看完整更新日志：[CHANGELOG.md](CHANGELOG.md)


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



## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 如何贡献

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

### 开发环境

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 查看测试覆盖率
pytest --cov=src --cov-report=html
```

## 📄 许可证

本项目仅供学习交流使用，请勿用于商业用途。

## 🙏 致谢

感谢所有贡献者和使用者的支持！

### 特别感谢

- 感谢star⭐和follow📰
- 欢迎PR和Issue
- 如果此项目对您有帮助，请考虑赞助支持 ☕

<div align="center">
  <img src="./author/wx_pay.png" width="350px" alt="微信赞赏码"> 
  <img src="./author/zfb_pay.jpg" width="350px" alt="支付宝收款码">
</div>

## 📈 Star 趋势

<a href="https://www.star-history.com/#cv-cat/Spider_XHS&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=cv-cat/Spider_XHS&type=Date" />
 </picture>
</a>

## 💬 交流群

<div align="center">
  <img width="400" alt="微信交流群" src="https://github.com/user-attachments/assets/ea690f33-0c5f-4941-9332-de9feff838e7" />
</div>

---

<div align="center">
  <p><strong>如果这个项目对你有帮助，请给一个Star⭐</strong></p>
  <p>Made with ❤️ by cv-cat</p>
</div>
