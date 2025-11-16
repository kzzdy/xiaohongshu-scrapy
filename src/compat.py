"""
兼容层 (Compatibility Layer)

提供旧版API到新版API的映射，确保向后兼容。
"""

import warnings
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from src.core.config import ConfigManager, SpiderConfig
from src.spider.note_spider import NoteSpider
from src.spider.user_spider import UserSpider
from src.spider.search_spider import SearchSpider


class LegacyAPIWrapper:
    """
    旧版API包装器

    将旧版本的API调用映射到新的模块化架构。
    保持接口签名不变，内部使用新API实现。
    """

    def __init__(self, cookies_str: str = None, proxies: Dict[str, str] = None):
        """
        初始化兼容层

        Args:
            cookies_str: Cookie字符串（可选，优先从环境变量读取）
            proxies: 代理配置（可选）
        """
        # 尝试从环境变量加载配置
        try:
            config_manager = ConfigManager()
            self.config = config_manager.load_config()

            # 如果提供了cookies_str，覆盖配置
            if cookies_str:
                self.config.cookies = cookies_str

            # 如果提供了proxies，覆盖配置
            if proxies:
                self.config.proxy = proxies

        except Exception as e:
            # 如果环境变量加载失败，使用传入的参数创建配置
            if not cookies_str:
                raise ValueError("必须提供cookies_str或配置.env文件") from e

            self.config = SpiderConfig(cookies=cookies_str, proxy=proxies)

        # 初始化爬虫实例
        self.note_spider = NoteSpider(self.config)
        self.user_spider = UserSpider(self.config)
        self.search_spider = SearchSpider(self.config)

    def spider_note(
        self, note_url: str, cookies_str: str = None, proxies: Dict[str, str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        爬取单个笔记（兼容旧版API）

        Args:
            note_url: 笔记URL
            cookies_str: Cookie字符串（可选）
            proxies: 代理配置（可选）

        Returns:
            (success, message, note_info)
        """
        warnings.warn(
            "spider_note 是旧版API，建议使用 NoteSpider.crawl_note",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            note_info = self.note_spider.crawl_note(note_url)
            return True, "Success", note_info
        except Exception as e:
            return False, str(e), None

    def spider_some_note(
        self,
        notes: List[str],
        cookies_str: str,
        base_path: Dict[str, str],
        save_choice: str,
        excel_name: str = "",
        proxies: Dict[str, str] = None,
    ) -> None:
        """
        爬取多个笔记（兼容旧版API）

        Args:
            notes: 笔记URL列表
            cookies_str: Cookie字符串
            base_path: 保存路径字典 {'excel': path, 'media': path}
            save_choice: 保存选项 'all'/'excel'/'media'
            excel_name: Excel文件名
            proxies: 代理配置
        """
        warnings.warn(
            "spider_some_note 是旧版API，建议使用 NoteSpider.crawl_notes_batch",
            DeprecationWarning,
            stacklevel=2,
        )

        # 映射保存选项
        save_media = save_choice in ["all", "media", "media-video", "media-image"]
        save_excel = save_choice in ["all", "excel"]

        # 确定输出格式
        if save_excel:
            save_format = "excel"
        else:
            save_format = None

        # 爬取笔记
        note_list = []
        for note_url in notes:
            try:
                note_info = self.note_spider.crawl_note(note_url)
                note_list.append(note_info)
            except Exception as e:
                print(f"爬取笔记失败 {note_url}: {e}")

        # 下载媒体文件
        if save_media and "media" in base_path:
            media_dir = base_path["media"]
            for note_info in note_list:
                try:
                    self.note_spider.download_media(
                        note_info,
                        output_dir=media_dir,
                        download_video="video" in save_choice
                        or save_choice == "all"
                        or save_choice == "media",
                        download_image="image" in save_choice
                        or save_choice == "all"
                        or save_choice == "media",
                    )
                except Exception as e:
                    print(f"下载媒体文件失败: {e}")

        # 导出Excel
        if save_excel and excel_name and "excel" in base_path:
            from src.data.exporter import DataExporter, ExportFormat

            exporter = DataExporter(output_dir=base_path["excel"])
            try:
                exporter.export(note_list, f"{excel_name}.xlsx", format=ExportFormat.EXCEL)
            except Exception as e:
                print(f"导出Excel失败: {e}")

    def spider_user_all_note(
        self,
        user_url: str,
        cookies_str: str,
        base_path: Dict[str, str],
        save_choice: str,
        excel_name: str = "",
        proxies: Dict[str, str] = None,
    ) -> Tuple[List[str], bool, str]:
        """
        爬取用户所有笔记（兼容旧版API）

        Args:
            user_url: 用户URL
            cookies_str: Cookie字符串
            base_path: 保存路径字典
            save_choice: 保存选项
            excel_name: Excel文件名
            proxies: 代理配置

        Returns:
            (note_list, success, message)
        """
        warnings.warn(
            "spider_user_all_note 是旧版API，建议使用 UserSpider.crawl_user_notes",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            # 映射保存选项
            save_media = save_choice in ["all", "media", "media-video", "media-image"]
            save_excel = save_choice in ["all", "excel"]

            save_format = "excel" if save_excel else None

            # 如果没有提供excel_name，从URL提取
            if not excel_name and save_excel:
                excel_name = user_url.split("/")[-1].split("?")[0]

            # 爬取用户笔记
            note_urls = self.user_spider.crawl_user_notes(
                user_url,
                save_format=save_format,
                output_name=excel_name,
                save_media=save_media,
                output_dir=base_path.get("media") if save_media else None,
            )

            return note_urls, True, "Success"

        except Exception as e:
            return [], False, str(e)

    def spider_some_search_note(
        self,
        query: str,
        require_num: int,
        cookies_str: str,
        base_path: Dict[str, str],
        save_choice: str,
        sort_type_choice: int = 0,
        note_type: int = 0,
        note_time: int = 0,
        note_range: int = 0,
        pos_distance: int = 0,
        geo: Dict[str, float] = None,
        excel_name: str = "",
        proxies: Dict[str, str] = None,
    ) -> Tuple[List[str], bool, str]:
        """
        搜索笔记（兼容旧版API）

        Args:
            query: 搜索关键词
            require_num: 搜索数量
            cookies_str: Cookie字符串
            base_path: 保存路径字典
            save_choice: 保存选项
            sort_type_choice: 排序方式
            note_type: 笔记类型
            note_time: 笔记时间
            note_range: 笔记范围
            pos_distance: 位置距离
            geo: 地理位置
            excel_name: Excel文件名
            proxies: 代理配置

        Returns:
            (note_list, success, message)
        """
        warnings.warn(
            "spider_some_search_note 是旧版API，建议使用 SearchSpider.search_notes",
            DeprecationWarning,
            stacklevel=2,
        )

        try:
            # 映射保存选项
            save_media = save_choice in ["all", "media", "media-video", "media-image"]
            save_excel = save_choice in ["all", "excel"]

            save_format = "excel" if save_excel else None

            # 如果没有提供excel_name，使用query
            if not excel_name and save_excel:
                excel_name = query

            # 搜索笔记
            note_urls = self.search_spider.search_notes(
                query=query,
                num=require_num,
                save_format=save_format,
                output_name=excel_name,
                sort_type=sort_type_choice,
                note_type=note_type,
                save_media=save_media,
                output_dir=base_path.get("media") if save_media else None,
            )

            return note_urls, True, "Success"

        except Exception as e:
            return [], False, str(e)


def create_legacy_spider(cookies_str: str = None, proxies: Dict[str, str] = None):
    """
    创建兼容旧版API的爬虫实例

    这是一个工厂函数，用于创建与旧版Data_Spider兼容的实例。

    Args:
        cookies_str: Cookie字符串（可选，优先从环境变量读取）
        proxies: 代理配置（可选）

    Returns:
        LegacyAPIWrapper实例

    Example:
        >>> spider = create_legacy_spider(cookies_str="your_cookies")
        >>> spider.spider_note(note_url, cookies_str)
    """
    return LegacyAPIWrapper(cookies_str, proxies)
