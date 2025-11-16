# 🚀 快速开始指南

## 一分钟上手

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖
npm install
```

### 2. 配置Cookie

**方法一：使用GUI配置（推荐）**

1. 启动GUI：`python gui_main.py` 或双击 `启动GUI.bat`
2. 在"配置"标签页点击"创建示例.env"
3. 点击"打开.env文件"
4. 将你的Cookie粘贴到 `COOKIES=` 后面
5. 保存文件并点击"重新加载配置"

**方法二：手动创建.env文件**

```bash
# 复制配置模板
cp .env.example .env

# 编辑.env文件
nano .env  # 或使用其他编辑器
```

在 `.env` 文件中填入：
```env
COOKIES='your_cookies_here'
RATE_LIMIT=3.0
TIMEOUT=30
RETRY_TIMES=3
```

### 3. 获取Cookie

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
11. 粘贴到.env文件中

## 使用方式

### 方式一：GUI图形界面（推荐新手）⭐

**启动GUI：**
```bash
python gui_main.py
```

或在Windows下双击 `启动GUI.bat` 文件

**推荐工作流程（三步走）：**

```
第一步：搜索爬取
  ├─ 输入关键词（如：重庆美食）
  ├─ 设置数量（建议10-50）
  ├─ 点击"开始搜索（仅保存JSON）"
  └─ JSON文件保存到 datas/json_datas/

第二步：JSON管理器
  ├─ 点击"刷新列表"
  ├─ 选择JSON文件
  ├─ 查看笔记列表
  └─ 点击"复制所有链接"

第三步：笔记爬取
  ├─ 粘贴链接（Ctrl+V）
  ├─ 选择保存格式（Excel/JSON/CSV）
  ├─ 勾选"下载图片/视频"
  └─ 点击"开始爬取"
```

详细说明请查看：[GUI使用说明](GUI使用说明.md) 或 [GUI快速开始](快速开始-GUI.md)

### 方式二：命令行界面（CLI）

**搜索笔记：**
```bash
python -m src.cli.main search "美食" --num 10 --format excel
```

**爬取用户笔记：**
```bash
python -m src.cli.main user <user_url> --format json
```

**爬取指定笔记：**
```bash
python -m src.cli.main note <note_url> --save-media
```

**查看帮助：**
```bash
python -m src.cli.main --help
```

### 方式三：Python API

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

## 输出文件

所有数据保存在 `datas` 目录：

```
datas/
├── excel_datas/    # Excel文件
├── json_datas/     # JSON文件（搜索结果）
├── csv_datas/      # CSV文件
└── media_datas/    # 媒体文件（图片/视频）
    └── 笔记标题_笔记ID/
        ├── detail.txt
        ├── image_1.jpg
        └── video_1.mp4
```

## 常见问题

### Q: 提示"配置加载失败"？
A: 检查Cookie是否正确填写，是否已过期

### Q: 爬取失败或没有数据？
A: 
1. 检查Cookie是否有效（重新获取）
2. 检查网络连接
3. 降低速率限制（增大RATE_LIMIT的值）
4. 查看日志页面的错误详情

### Q: 如何提高爬取速度？
A: 在.env中适当提高速率限制：
```env
RATE_LIMIT=5.0  # 每秒5个请求（不要太高）
```

### Q: 下载的文件在哪里？
A: 默认在项目根目录的 `datas` 文件夹

## 详细文档

- **GUI使用说明**: [GUI使用说明.md](GUI使用说明.md)
- **GUI快速开始**: [快速开始-GUI.md](快速开始-GUI.md)
- **迁移指南**: [MIGRATION.md](MIGRATION.md)
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)
- **项目主文档**: [README.md](README.md)

## 需要帮助？

1. 查看日志页面的错误信息
2. 阅读详细文档
3. 在GitHub上提交Issue
4. 加入交流群获取帮助

---

**祝你使用愉快！** 🎉
