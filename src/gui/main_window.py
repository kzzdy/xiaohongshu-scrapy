"""主GUI窗口"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
from pathlib import Path
from typing import Optional
import sys
import os

# 添加项目根目录到Python路径（支持直接运行此文件）
# 获取项目根目录（当前文件的上上级目录）
_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.core.config import ConfigManager, ConfigError
from src.core.progress import ProgressManager
from src.spider.note_spider import NoteSpider
from src.spider.user_spider import UserSpider
from src.spider.search_spider import SearchSpider


class SpiderGUI:
    """小红书爬虫GUI主窗口"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("小红书爬虫工具 - Spider XHS")
        self.root.geometry("900x700")
        
        # 配置管理器
        self.config_manager = ConfigManager()
        self.config = None
        
        # 爬虫实例
        self.note_spider: Optional[NoteSpider] = None
        self.user_spider: Optional[UserSpider] = None
        self.search_spider: Optional[SearchSpider] = None
        
        # 日志队列
        self.log_queue = queue.Queue()
        
        # 创建UI
        self._create_widgets()
        self._load_config()
        
        # 启动日志更新
        self._update_log()

    def _create_widgets(self):
        """创建UI组件"""
        # 创建笔记本（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个标签页（按使用流程排序）
        self._create_config_tab()      # 1. 配置
        self._create_search_tab()      # 2. 搜索爬取（获取JSON）
        self._create_user_tab()        # 3. JSON管理器（提取链接）
        self._create_note_tab()        # 4. 笔记爬取（下载详情）
        self._create_log_tab()         # 5. 日志
        
        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_config_tab(self):
        """创建配置标签页"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ 配置")
        
        # 配置说明
        info_frame = ttk.LabelFrame(config_frame, text="配置说明", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = """
        请在项目根目录的 .env 文件中配置以下信息：
        
        必填项：
        • COOKIES - 小红书登录Cookie（必须）
        
        可选项：
        • RATE_LIMIT - 请求速率限制（默认3.0请求/秒）
        • RETRY_TIMES - 重试次数（默认3次）
        • TIMEOUT - 请求超时时间（默认30秒）
        • OUTPUT_DIR - 输出目录（默认datas）
        • LOG_LEVEL - 日志级别（默认INFO）
        
        配置完成后点击"重新加载配置"按钮
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack()
        
        # 配置状态
        status_frame = ttk.LabelFrame(config_frame, text="配置状态", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.config_status_label = ttk.Label(status_frame, text="未加载配置", foreground="red")
        self.config_status_label.pack()
        
        # 按钮
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="重新加载配置", command=lambda: self._load_config(show_error_dialog=True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="打开.env文件", command=self._open_env_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="创建示例.env", command=self._create_example_env).pack(side=tk.LEFT, padx=5)

    def _create_note_tab(self):
        """创建笔记爬取标签页"""
        note_frame = ttk.Frame(self.notebook)
        self.notebook.add(note_frame, text="📝 笔记爬取")
        
        # 输入区域
        input_frame = ttk.LabelFrame(note_frame, text="笔记URL", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(input_frame, text="请输入笔记URL（每行一个）：").pack(anchor=tk.W)
        
        self.note_urls_text = scrolledtext.ScrolledText(input_frame, height=10)
        self.note_urls_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.note_urls_text.insert(tk.END, "https://www.xiaohongshu.com/explore/...")
        
        # 选项
        options_frame = ttk.Frame(note_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(options_frame, text="保存格式：").pack(side=tk.LEFT)
        self.note_format_var = tk.StringVar(value="json")
        ttk.Radiobutton(options_frame, text="JSON", variable=self.note_format_var, value="json").pack(side=tk.LEFT)
        ttk.Radiobutton(options_frame, text="CSV", variable=self.note_format_var, value="csv").pack(side=tk.LEFT)
        ttk.Radiobutton(options_frame, text="Excel", variable=self.note_format_var, value="excel").pack(side=tk.LEFT)
        
        self.note_download_media_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="下载图片/视频", variable=self.note_download_media_var).pack(side=tk.LEFT, padx=20)
        
        # 按钮
        button_frame = ttk.Frame(note_frame)
        button_frame.pack(pady=10)
        
        self.note_start_btn = ttk.Button(button_frame, text="开始爬取", command=self._start_note_crawl)
        self.note_start_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="清空输入", command=lambda: self.note_urls_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)

    def _create_user_tab(self):
        """创建 JSON 管理器标签页"""
        user_frame = ttk.Frame(self.notebook)
        self.notebook.add(user_frame, text="📁 JSON 管理器")
        
        # 说明
        info_frame = ttk.LabelFrame(user_frame, text="使用说明", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = """
        1. 点击"刷新列表"加载 datas/json_datas 目录下的 JSON 文件
        2. 在左侧列表中选择一个 JSON 文件
        3. 右侧会显示该文件中的所有笔记（标题 + 链接）
        4. 点击"复制所有链接"可以复制到剪贴板
        5. 切换到"笔记爬取"标签页，粘贴链接进行爬取
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # 主内容区域
        content_frame = ttk.Frame(user_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：JSON 文件列表
        left_frame = ttk.LabelFrame(content_frame, text="JSON 文件列表", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
        # 文件列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.json_listbox = tk.Listbox(list_frame, width=40, yscrollcommand=scrollbar.set)
        self.json_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.json_listbox.yview)
        
        # 绑定选择事件
        self.json_listbox.bind('<<ListboxSelect>>', self._on_json_file_select)
        
        # 按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="刷新列表", command=self._refresh_json_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="打开目录", command=self._open_datas_dir).pack(side=tk.LEFT, padx=2)
        
        # 右侧：笔记列表
        right_frame = ttk.LabelFrame(content_frame, text="笔记列表", padding=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 笔记列表显示区域
        self.notes_text = scrolledtext.ScrolledText(right_frame, height=20, width=60)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮
        notes_btn_frame = ttk.Frame(right_frame)
        notes_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(notes_btn_frame, text="复制所有链接", command=self._copy_all_urls).pack(side=tk.LEFT, padx=2)
        ttk.Button(notes_btn_frame, text="复制选中链接", command=self._copy_selected_urls).pack(side=tk.LEFT, padx=2)
        ttk.Button(notes_btn_frame, text="清空", command=lambda: self.notes_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=2)
        
        # 初始加载
        self._refresh_json_list()

    def _create_search_tab(self):
        """创建搜索标签页"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="🔍 搜索爬取")
        
        # 说明
        info_frame = ttk.LabelFrame(search_frame, text="功能说明", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = """
        搜索爬取用于获取笔记列表（保存为JSON到 datas/json_datas/ 目录），不下载图片/视频。
        工作流程：搜索 → 保存JSON → JSON管理器提取链接 → 笔记爬取下载完整内容
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # 搜索参数
        params_frame = ttk.LabelFrame(search_frame, text="搜索参数", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 关键词
        keyword_frame = ttk.Frame(params_frame)
        keyword_frame.pack(fill=tk.X, pady=5)
        ttk.Label(keyword_frame, text="搜索关键词：").pack(side=tk.LEFT)
        self.search_keyword_entry = ttk.Entry(keyword_frame, width=50)
        self.search_keyword_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(keyword_frame, text="（如：重庆美食、用户昵称等）").pack(side=tk.LEFT)
        
        # 数量
        num_frame = ttk.Frame(params_frame)
        num_frame.pack(fill=tk.X, pady=5)
        ttk.Label(num_frame, text="爬取数量：").pack(side=tk.LEFT)
        self.search_num_var = tk.IntVar(value=20)
        ttk.Spinbox(num_frame, from_=1, to=1000, textvariable=self.search_num_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(num_frame, text="（建议10-50，避免触发风控）").pack(side=tk.LEFT)
        
        # 排序方式
        sort_frame = ttk.Frame(params_frame)
        sort_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sort_frame, text="排序方式：").pack(side=tk.LEFT)
        self.search_sort_var = tk.StringVar(value="general")
        ttk.Radiobutton(sort_frame, text="综合", variable=self.search_sort_var, value="general").pack(side=tk.LEFT)
        ttk.Radiobutton(sort_frame, text="最新", variable=self.search_sort_var, value="time_descending").pack(side=tk.LEFT)
        ttk.Radiobutton(sort_frame, text="最热", variable=self.search_sort_var, value="popularity_descending").pack(side=tk.LEFT)
        
        # 按钮
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(pady=10)
        
        self.search_start_btn = ttk.Button(button_frame, text="开始搜索（仅保存JSON）", command=self._start_search_crawl, width=25)
        self.search_start_btn.pack(side=tk.LEFT, padx=5)
        
        # 提示
        tip_frame = ttk.LabelFrame(search_frame, text="💡 提示", padding=10)
        tip_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tip_text = """
        • 搜索完成后，JSON文件会保存到 datas/json_datas/ 目录
        • 切换到【JSON管理器】标签页查看和提取笔记链接
        • 然后在【笔记爬取】标签页下载完整内容（图片/视频）
        """
        ttk.Label(tip_frame, text=tip_text, justify=tk.LEFT, foreground="blue").pack()

    def _create_log_tab(self):
        """创建日志标签页"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📋 日志")
        
        # 日志显示区域
        self.log_text = scrolledtext.ScrolledText(log_frame, height=30, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="清空日志", command=self._clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存日志", command=self._save_log).pack(side=tk.LEFT, padx=5)

    def _load_config(self, show_error_dialog=False):
        """加载配置
        
        Args:
            show_error_dialog: 是否显示错误对话框（默认False，避免启动时弹窗）
        """
        try:
            self.config = self.config_manager.load_config()
            
            # 创建API客户端和相关组件
            from src.api.xhs_pc import XHSPCApi
            from src.core.rate_limiter import RateLimiter
            from src.core.error_handler import ErrorHandler
            from src.data.processor import DataProcessor
            from src.data.exporter import DataExporter
            
            self.log("正在初始化组件...")
            
            rate_limiter = RateLimiter(rate=self.config.rate_limit)
            error_handler = ErrorHandler(
                log_level=self.config.log_level,
                log_dir="logs"
            )
            progress_manager = ProgressManager(progress_file=self.config.progress_file)
            
            self.log("正在创建API客户端...")
            
            api_client = XHSPCApi(
                cookies_str=self.config.cookies,
                rate_limiter=rate_limiter,
                error_handler=error_handler,
                timeout=self.config.timeout,
                proxies=self.config.proxy,
            )
            
            data_processor = DataProcessor()
            data_exporter = DataExporter(output_dir=self.config.output_dir)
            
            self.log("正在初始化爬虫...")
            
            # 初始化爬虫实例
            self.note_spider = NoteSpider(
                api_client=api_client,
                progress_manager=progress_manager,
                data_processor=data_processor,
                data_exporter=data_exporter,
            )
            
            self.user_spider = UserSpider(
                api_client=api_client,
                data_processor=data_processor,
                data_exporter=data_exporter,
                note_spider=self.note_spider,
            )
            
            self.search_spider = SearchSpider(
                api_client=api_client,
                progress_manager=progress_manager,
                data_processor=data_processor,
                data_exporter=data_exporter,
                note_spider=self.note_spider,
            )
            
            self.config_status_label.config(text="✓ 配置加载成功", foreground="green")
            self.log("✓ 配置加载成功")
            self.log(f"输出目录: {self.config.output_dir}")
            self.log(f"速率限制: {self.config.rate_limit} 请求/秒")
            
        except ConfigError as e:
            self.config_status_label.config(text=f"✗ 配置加载失败", foreground="red")
            self.log(f"✗ 配置加载失败: {str(e)}", level="ERROR")
            self.log("请在配置页面创建并配置.env文件", level="WARNING")
            
            # 只在用户主动点击"重新加载配置"时才显示错误对话框
            if show_error_dialog:
                messagebox.showerror("配置错误", str(e))
        except Exception as e:
            self.config_status_label.config(text=f"✗ 初始化失败", foreground="red")
            self.log(f"✗ 初始化失败: {str(e)}", level="ERROR")
            import traceback
            self.log(traceback.format_exc(), level="ERROR")
            
            if show_error_dialog:
                messagebox.showerror("初始化错误", f"初始化失败: {str(e)}")

    def _open_env_file(self):
        """打开.env文件"""
        env_path = Path(".env")
        if env_path.exists():
            import os
            import subprocess
            
            try:
                if sys.platform == "win32":
                    # Windows: 使用默认程序打开
                    os.startfile(str(env_path))
                elif sys.platform == "darwin":
                    # macOS: 使用open命令
                    subprocess.run(["open", str(env_path)])
                else:
                    # Linux: 使用xdg-open
                    subprocess.run(["xdg-open", str(env_path)])
                
                self.log("已打开.env文件")
            except Exception as e:
                self.log(f"打开文件失败: {str(e)}", level="ERROR")
                error_msg = f"无法自动打开.env文件\n\n错误: {str(e)}\n\n请手动打开项目根目录下的.env文件进行编辑"
                messagebox.showerror("打开失败", error_msg)
        else:
            msg = ".env文件不存在\n\n请先点击'创建示例.env'按钮创建配置文件"
            messagebox.showwarning("文件不存在", msg)

    def _create_example_env(self):
        """创建示例.env文件"""
        example_content = """# 小红书爬虫配置文件

# ===== 必填配置 =====
# 小红书Cookie（必须配置）
COOKIES=your_cookies_here

# ===== 可选配置 =====
# 请求速率限制（请求/秒）
RATE_LIMIT=3.0

# 重试次数
RETRY_TIMES=3

# 请求超时时间（秒）
TIMEOUT=30

# 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
LOG_LEVEL=INFO

# 输出目录
OUTPUT_DIR=datas

# 进度文件路径
PROGRESS_FILE=datas/.progress.json

# 是否启用断点续传
ENABLE_RESUME=true

# 是否下载媒体文件
DOWNLOAD_MEDIA=true

# 最大并发下载数
MAX_CONCURRENT_DOWNLOADS=3

# ===== 代理配置（可选） =====
# HTTP_PROXY=http://127.0.0.1:7890
# HTTPS_PROXY=http://127.0.0.1:7890
"""
        
        env_path = Path(".env")
        if env_path.exists():
            if not messagebox.askyesno("文件已存在", ".env文件已存在，是否覆盖？"):
                return
        
        env_path.write_text(example_content, encoding="utf-8")
        self.log(".env示例文件创建成功")
        messagebox.showinfo("成功", ".env示例文件创建成功，请编辑并填入你的Cookie")

    def _start_note_crawl(self):
        """开始笔记爬取"""
        if not self._check_config():
            return
        
        urls_text = self.note_urls_text.get(1.0, tk.END).strip()
        if not urls_text:
            messagebox.showwarning("输入错误", "请输入至少一个笔记URL")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        save_format = self.note_format_var.get()
        download_media = self.note_download_media_var.get()
        
        # 将save_format转换为ExportFormat
        from src.data.exporter import ExportFormat
        format_map = {
            "json": ExportFormat.JSON,
            "csv": ExportFormat.CSV,
            "excel": ExportFormat.EXCEL
        }
        export_format = format_map.get(save_format, ExportFormat.EXCEL)
        
        self.note_start_btn.config(state=tk.DISABLED)
        self.log(f"开始爬取 {len(urls)} 个笔记...")
        self.log(f"保存格式: {save_format.upper()}, 下载媒体: {'是' if download_media else '否'}")
        
        def crawl_task():
            try:
                notes = []
                for i, url in enumerate(urls, 1):
                    self.log(f"[{i}/{len(urls)}] 爬取笔记: {url}")
                    note_info = self.note_spider.crawl_note(
                        url,
                        save_media=download_media,
                        export_format=None  # 单个笔记不导出，批量导出
                    )
                    if note_info:
                        notes.append(note_info)
                        self.log(f"✓ 笔记爬取成功: {note_info.get('title', 'N/A')}")
                    else:
                        self.log(f"✗ 笔记爬取失败", level="ERROR")
                
                # 批量导出所有笔记
                if notes and export_format:
                    from datetime import datetime
                    filename = f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    filepath = self.note_spider.exporter.export_notes(notes, filename, export_format)
                    self.log(f"✓ 数据已导出到: {filepath}")
                
                self.log(f"所有笔记爬取完成！成功: {len(notes)}/{len(urls)}")
                messagebox.showinfo("完成", f"成功爬取 {len(notes)}/{len(urls)} 个笔记\n\n文件保存在: {self.config.output_dir}")
            except Exception as e:
                self.log(f"爬取过程出错: {str(e)}", level="ERROR")
                import traceback
                self.log(traceback.format_exc(), level="ERROR")
                messagebox.showerror("错误", f"爬取失败: {str(e)}")
            finally:
                self.note_start_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=crawl_task, daemon=True).start()

    def _refresh_json_list(self):
        """刷新 JSON 文件列表"""
        try:
            # 清空列表
            self.json_listbox.delete(0, tk.END)
            
            # 查找 JSON 文件
            json_dir = Path("datas/json_datas")
            if not json_dir.exists():
                self.log("JSON 目录不存在，请先使用搜索功能生成 JSON 文件", level="WARNING")
                return
            
            json_files = list(json_dir.glob("*.json"))
            
            if not json_files:
                self.log("未找到 JSON 文件", level="WARNING")
                self.json_listbox.insert(tk.END, "（暂无 JSON 文件）")
                return
            
            # 按修改时间排序（最新的在前）
            json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 添加到列表
            for json_file in json_files:
                # 显示文件名和修改时间
                mtime = json_file.stat().st_mtime
                from datetime import datetime
                time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                display_name = f"{json_file.name} ({time_str})"
                self.json_listbox.insert(tk.END, display_name)
            
            self.log(f"找到 {len(json_files)} 个 JSON 文件")
            
        except Exception as e:
            self.log(f"刷新文件列表失败: {str(e)}", level="ERROR")
            messagebox.showerror("错误", f"刷新失败: {str(e)}")
    
    def _on_json_file_select(self, event):
        """JSON 文件选择事件"""
        selection = self.json_listbox.curselection()
        if not selection:
            return
        
        try:
            # 获取选中的文件名
            display_name = self.json_listbox.get(selection[0])
            if display_name == "（暂无 JSON 文件）":
                return
            
            # 提取文件名（去掉时间部分）
            filename = display_name.split(" (")[0]
            json_path = Path("datas/json_datas") / filename
            
            if not json_path.exists():
                self.log(f"文件不存在: {json_path}", level="ERROR")
                return
            
            # 读取 JSON 文件
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                notes_data = json.load(f)
            
            # 清空显示区域
            self.notes_text.delete(1.0, tk.END)
            
            # 显示笔记列表
            if isinstance(notes_data, list):
                self.notes_text.insert(tk.END, f"文件: {filename}\n")
                self.notes_text.insert(tk.END, f"笔记数量: {len(notes_data)}\n")
                self.notes_text.insert(tk.END, "=" * 80 + "\n\n")
                
                for idx, note in enumerate(notes_data, 1):
                    title = note.get('title', '无标题')
                    note_url = note.get('note_url', '')
                    note_id = note.get('note_id', '')
                    
                    self.notes_text.insert(tk.END, f"{idx}. {title}\n")
                    self.notes_text.insert(tk.END, f"   链接: {note_url}\n")
                    self.notes_text.insert(tk.END, f"   ID: {note_id}\n\n")
                
                self.log(f"加载了 {len(notes_data)} 个笔记")
            else:
                self.notes_text.insert(tk.END, "JSON 格式不正确（应该是笔记数组）\n")
                self.log("JSON 格式不正确", level="WARNING")
                
        except Exception as e:
            self.log(f"加载 JSON 文件失败: {str(e)}", level="ERROR")
            messagebox.showerror("错误", f"加载失败: {str(e)}")
    
    def _copy_all_urls(self):
        """复制所有笔记链接"""
        try:
            content = self.notes_text.get(1.0, tk.END)
            
            # 提取所有链接
            import re
            urls = re.findall(r'链接: (https://[^\s]+)', content)
            
            if not urls:
                messagebox.showwarning("提示", "没有找到链接")
                return
            
            # 复制到剪贴板
            urls_text = '\n'.join(urls)
            self.root.clipboard_clear()
            self.root.clipboard_append(urls_text)
            
            self.log(f"已复制 {len(urls)} 个链接到剪贴板")
            messagebox.showinfo("成功", f"已复制 {len(urls)} 个链接到剪贴板\n\n可以切换到【笔记爬取】标签页粘贴使用")
            
        except Exception as e:
            self.log(f"复制链接失败: {str(e)}", level="ERROR")
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def _copy_selected_urls(self):
        """复制选中的链接"""
        try:
            # 获取选中的文本
            try:
                selected_text = self.notes_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                messagebox.showwarning("提示", "请先选中要复制的文本")
                return
            
            # 提取链接
            import re
            urls = re.findall(r'https://[^\s]+', selected_text)
            
            if not urls:
                messagebox.showwarning("提示", "选中的文本中没有找到链接")
                return
            
            # 复制到剪贴板
            urls_text = '\n'.join(urls)
            self.root.clipboard_clear()
            self.root.clipboard_append(urls_text)
            
            self.log(f"已复制 {len(urls)} 个链接到剪贴板")
            messagebox.showinfo("成功", f"已复制 {len(urls)} 个链接")
            
        except Exception as e:
            self.log(f"复制链接失败: {str(e)}", level="ERROR")
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def _open_datas_dir(self):
        """打开 JSON 目录"""
        try:
            datas_dir = Path("datas/json_datas")
            datas_dir.mkdir(parents=True, exist_ok=True)
            
            import os
            import subprocess
            
            if sys.platform == "win32":
                os.startfile(str(datas_dir))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(datas_dir)])
            else:
                subprocess.run(["xdg-open", str(datas_dir)])
            
            self.log(f"已打开目录: {datas_dir}")
            
        except Exception as e:
            self.log(f"打开目录失败: {str(e)}", level="ERROR")
            messagebox.showerror("错误", f"打开目录失败: {str(e)}")

    def _start_search_crawl(self):
        """开始搜索爬取（仅保存JSON，不下载媒体）"""
        if not self._check_config():
            return
        
        keyword = self.search_keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("输入错误", "请输入搜索关键词")
            return
        
        num = self.search_num_var.get()
        sort = self.search_sort_var.get()
        
        self.search_start_btn.config(state=tk.DISABLED)
        self.log(f"开始搜索: {keyword} (数量: {num}, 排序: {sort})")
        self.log("注意：仅保存JSON文件，不下载图片/视频")
        
        def crawl_task():
            try:
                # 将sort字符串转换为sort_type整数
                sort_map = {
                    "general": SearchSpider.SORT_GENERAL,
                    "time_descending": SearchSpider.SORT_TIME,
                    "popularity_descending": SearchSpider.SORT_POPULARITY
                }
                sort_type = sort_map.get(sort, SearchSpider.SORT_GENERAL)
                
                # 强制使用JSON格式，不下载媒体
                from src.data.exporter import ExportFormat
                
                # 使用crawl_search_notes，强制JSON格式，不下载媒体
                notes = self.search_spider.crawl_search_notes(
                    query=keyword,
                    num=num,
                    sort_type=sort_type,
                    save_media=False,  # 强制不下载媒体
                    export_format=ExportFormat.JSON,  # 强制JSON格式
                    use_progress=True
                )
                
                self.log(f"✓ 搜索爬取完成！获取 {len(notes)} 个笔记")
                self.log(f"✓ JSON文件已保存到: datas/json_datas/search_{keyword}_*.json")
                self.log("→ 下一步：切换到【JSON管理器】标签页提取笔记链接")
                
                messagebox.showinfo(
                    "完成", 
                    f"搜索爬取完成！\n\n"
                    f"获取笔记数: {len(notes)}\n"
                    f"保存位置: datas/json_datas/\n\n"
                    f"下一步：\n"
                    f"1. 切换到【JSON管理器】标签页\n"
                    f"2. 刷新列表并选择JSON文件\n"
                    f"3. 复制笔记链接\n"
                    f"4. 在【笔记爬取】标签页下载完整内容"
                )
            except Exception as e:
                self.log(f"搜索过程出错: {str(e)}", level="ERROR")
                import traceback
                self.log(traceback.format_exc(), level="ERROR")
                messagebox.showerror("错误", f"搜索失败: {str(e)}")
            finally:
                self.search_start_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=crawl_task, daemon=True).start()

    def _check_config(self):
        """检查配置是否已加载"""
        if self.config is None:
            messagebox.showwarning("配置未加载", "请先在配置页面加载配置")
            self.notebook.select(0)  # 切换到配置页面
            return False
        return True

    def log(self, message: str, level: str = "INFO"):
        """添加日志"""
        self.log_queue.put((message, level))

    def _update_log(self):
        """更新日志显示"""
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                
                self.log_text.config(state=tk.NORMAL)
                
                # 根据级别设置颜色
                if level == "ERROR":
                    tag = "error"
                    self.log_text.tag_config(tag, foreground="red")
                elif level == "WARNING":
                    tag = "warning"
                    self.log_text.tag_config(tag, foreground="orange")
                else:
                    tag = "info"
                    self.log_text.tag_config(tag, foreground="black")
                
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                log_line = f"[{timestamp}] {message}\n"
                
                self.log_text.insert(tk.END, log_line, tag)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
                
                # 更新状态栏
                self.status_bar.config(text=message[:100])
                
        except queue.Empty:
            pass
        
        # 每100ms检查一次
        self.root.after(100, self._update_log)

    def _clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _save_log(self):
        """保存日志"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            log_content = self.log_text.get(1.0, tk.END)
            Path(filename).write_text(log_content, encoding="utf-8")
            self.log(f"日志已保存到: {filename}")

    def run(self):
        """运行GUI"""
        self.log("小红书爬虫工具启动")
        self.log("请先在配置页面加载配置")
        self.root.mainloop()


def main():
    """GUI入口函数"""
    app = SpiderGUI()
    app.run()


if __name__ == "__main__":
    main()
