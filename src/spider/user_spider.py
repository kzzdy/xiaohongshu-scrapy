"""用户爬虫模块"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import urllib.parse
from loguru import logger

from src.api.xhs_pc import XHSPCApi
from src.data.processor import DataProcessor
from src.data.exporter import DataExporter, ExportFormat
from src.data.validator import DataValidator
from src.spider.note_spider import NoteSpider


class UserSpider:
    """用户爬虫

    负责爬取小红书用户信息，支持：
    - 用户信息爬取
    - 用户所有笔记爬取
    - 数据验证和导出
    """

    def __init__(
        self,
        api_client: XHSPCApi,
        data_processor: Optional[DataProcessor] = None,
        data_exporter: Optional[DataExporter] = None,
        note_spider: Optional[NoteSpider] = None,
    ):
        """初始化用户爬虫

        Args:
            api_client: 小红书PC端API客户端
            data_processor: 数据处理器（可选）
            data_exporter: 数据导出器（可选）
            note_spider: 笔记爬虫（可选，用于爬取用户笔记）
        """
        self.api = api_client
        self.processor = data_processor or DataProcessor()
        self.exporter = data_exporter or DataExporter()
        self.validator = DataValidator()
        self.note_spider = note_spider

    def fetch_user_info(self, user_url: str) -> Optional[Dict[str, Any]]:
        """获取用户信息

        Args:
            user_url: 用户主页URL

        Returns:
            处理后的用户信息字典，失败返回None
        """
        logger.info(f"Fetching user info: {user_url}")

        try:
            # 从URL中提取用户ID
            url_parse = urllib.parse.urlparse(user_url)
            user_id = url_parse.path.split("/")[-1]

            if not user_id:
                logger.error("Failed to extract user_id from URL")
                return None

            # 验证用户ID格式
            if not self.validator.validate_user_id(user_id):
                logger.warning(f"Invalid user_id format: {user_id}")

            # 调用API获取用户信息
            success, msg, res_json = self.api.get_user_info(user_id)

            if not success:
                logger.error(f"Failed to fetch user info: {msg}")
                return None

            # 检查响应数据
            if not res_json or "data" not in res_json:
                logger.error("Invalid response data")
                return None

            # 处理用户数据
            user_data = res_json["data"]
            processed_user = self.processor.handle_user_info(user_data, user_id)

            if not processed_user:
                logger.error("Failed to process user data")
                return None

            logger.info(f"Successfully fetched user: {processed_user['nickname']} ({user_id})")
            return processed_user

        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
            return None

    def fetch_user_notes(
        self,
        user_url: str,
        max_notes: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户所有笔记

        Args:
            user_url: 用户主页URL
            max_notes: 最大笔记数量（可选，None表示获取全部）

        Returns:
            笔记信息列表
        """
        logger.info(f"Fetching user notes: {user_url}")

        # 调用API获取用户所有笔记
        success, msg, note_list = self.api.get_user_all_notes(user_url)

        if not success:
            logger.error(f"Failed to fetch user notes: {msg}")
            return []

        logger.info(f"Found {len(note_list)} notes for user")

        # 限制笔记数量
        if max_notes and len(note_list) > max_notes:
            note_list = note_list[:max_notes]
            logger.info(f"Limited to {max_notes} notes")

        # 处理笔记数据
        processed_notes = []
        for idx, note_data in enumerate(note_list, 1):
            try:
                # 构建完整的笔记数据结构
                # API返回的是简化版本，需要转换为标准格式
                full_note_data = self._convert_user_note_to_full_note(note_data)

                # 处理笔记数据
                processed_note = self.processor.handle_note_info(full_note_data)

                if processed_note:
                    processed_notes.append(processed_note)
                    logger.debug(
                        f"[{idx}/{len(note_list)}] Processed note: {processed_note['note_id']}"
                    )
                else:
                    logger.warning(f"[{idx}/{len(note_list)}] Failed to process note")

            except Exception as e:
                logger.error(f"[{idx}/{len(note_list)}] Error processing note: {e}")

        logger.info(f"Successfully processed {len(processed_notes)}/{len(note_list)} notes")
        return processed_notes

    def _convert_user_note_to_full_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """将用户笔记数据转换为完整笔记数据格式

        Args:
            note_data: 用户笔记数据（简化版）

        Returns:
            完整笔记数据格式
        """
        # 构建标准的笔记数据结构
        note_id = note_data.get("note_id", "")

        full_note = {
            "id": note_id,
            "url": f"https://www.xiaohongshu.com/explore/{note_id}",
            "note_card": {
                "type": note_data.get("type", "normal"),
                "user": {
                    "user_id": note_data.get("user", {}).get("user_id", ""),
                    "nickname": note_data.get("user", {}).get("nickname", ""),
                    "avatar": note_data.get("user", {}).get("avatar", ""),
                },
                "title": note_data.get("display_title", ""),
                "desc": "",
                "interact_info": {
                    "liked_count": note_data.get("liked_count", 0),
                    "collected_count": 0,
                    "comment_count": 0,
                    "share_count": 0,
                },
                "image_list": [],
                "video": {},
                "tag_list": [],
                "time": note_data.get("time", 0),
                "ip_location": note_data.get("ip_location", "未知"),
            },
        }

        # 处理封面图片
        cover = note_data.get("cover", {})
        if cover:
            full_note["note_card"]["image_list"] = [
                {"info_list": [{}, {"url": cover.get("url", "")}]}
            ]

        return full_note

    def fetch_user_liked_notes(
        self,
        user_url: str,
        max_notes: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户喜欢的笔记

        Args:
            user_url: 用户主页URL
            max_notes: 最大笔记数量（可选）

        Returns:
            笔记信息列表
        """
        logger.info(f"Fetching user liked notes: {user_url}")

        # 调用API获取用户喜欢的笔记
        success, msg, note_list = self.api.get_user_all_like_note_info(user_url)

        if not success:
            logger.error(f"Failed to fetch user liked notes: {msg}")
            return []

        logger.info(f"Found {len(note_list)} liked notes for user")

        # 限制笔记数量
        if max_notes and len(note_list) > max_notes:
            note_list = note_list[:max_notes]
            logger.info(f"Limited to {max_notes} notes")

        # 处理笔记数据
        processed_notes = []
        for idx, note_data in enumerate(note_list, 1):
            try:
                full_note_data = self._convert_user_note_to_full_note(note_data)
                processed_note = self.processor.handle_note_info(full_note_data)

                if processed_note:
                    processed_notes.append(processed_note)
                    logger.debug(
                        f"[{idx}/{len(note_list)}] Processed liked note: {processed_note['note_id']}"
                    )

            except Exception as e:
                logger.error(f"[{idx}/{len(note_list)}] Error processing liked note: {e}")

        logger.info(f"Successfully processed {len(processed_notes)}/{len(note_list)} liked notes")
        return processed_notes

    def fetch_user_collected_notes(
        self,
        user_url: str,
        max_notes: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户收藏的笔记

        Args:
            user_url: 用户主页URL
            max_notes: 最大笔记数量（可选）

        Returns:
            笔记信息列表
        """
        logger.info(f"Fetching user collected notes: {user_url}")

        # 调用API获取用户收藏的笔记
        success, msg, note_list = self.api.get_user_all_collect_note_info(user_url)

        if not success:
            logger.error(f"Failed to fetch user collected notes: {msg}")
            return []

        logger.info(f"Found {len(note_list)} collected notes for user")

        # 限制笔记数量
        if max_notes and len(note_list) > max_notes:
            note_list = note_list[:max_notes]
            logger.info(f"Limited to {max_notes} notes")

        # 处理笔记数据
        processed_notes = []
        for idx, note_data in enumerate(note_list, 1):
            try:
                full_note_data = self._convert_user_note_to_full_note(note_data)
                processed_note = self.processor.handle_note_info(full_note_data)

                if processed_note:
                    processed_notes.append(processed_note)
                    logger.debug(
                        f"[{idx}/{len(note_list)}] Processed collected note: {processed_note['note_id']}"
                    )

            except Exception as e:
                logger.error(f"[{idx}/{len(note_list)}] Error processing collected note: {e}")

        logger.info(
            f"Successfully processed {len(processed_notes)}/{len(note_list)} collected notes"
        )
        return processed_notes

    def crawl_user(
        self,
        user_url: str,
        fetch_notes: bool = False,
        max_notes: Optional[int] = None,
        save_media: bool = False,
        export_format: Optional[ExportFormat] = None,
    ) -> Optional[Dict[str, Any]]:
        """爬取用户信息（完整流程）

        Args:
            user_url: 用户主页URL
            fetch_notes: 是否获取用户笔记
            max_notes: 最大笔记数量（可选）
            save_media: 是否保存媒体文件（需要note_spider）
            export_format: 导出格式（可选）

        Returns:
            包含用户信息和笔记的字典，失败返回None
        """
        result = {}

        # 获取用户信息
        user_info = self.fetch_user_info(user_url)

        if not user_info:
            return None

        result["user"] = user_info

        # 获取用户笔记
        if fetch_notes:
            notes = self.fetch_user_notes(user_url, max_notes)
            result["notes"] = notes

            logger.info(f"Fetched {len(notes)} notes for user {user_info['nickname']}")

            # 下载媒体文件
            if save_media and self.note_spider and notes:
                logger.info(f"Downloading media files for {len(notes)} notes")
                for note in notes:
                    try:
                        self.note_spider.download_media(note)
                    except Exception as e:
                        logger.error(f"Failed to download media for note {note['note_id']}: {e}")

            # 导出笔记数据
            if export_format and notes:
                filename = f"user_{user_info['user_id']}_notes"
                filepath = self.exporter.export_notes(notes, filename, export_format)
                logger.info(f"Exported {len(notes)} notes to {filepath}")

        # 导出用户信息
        if export_format:
            filename = f"user_{user_info['user_id']}_info"
            filepath = self.exporter.export_users([user_info], filename, export_format)
            logger.info(f"Exported user info to {filepath}")

        return result

    def crawl_users(
        self,
        user_urls: List[str],
        fetch_notes: bool = False,
        max_notes: Optional[int] = None,
        export_format: Optional[ExportFormat] = None,
    ) -> List[Dict[str, Any]]:
        """批量爬取用户信息

        Args:
            user_urls: 用户主页URL列表
            fetch_notes: 是否获取用户笔记
            max_notes: 每个用户的最大笔记数量（可选）
            export_format: 导出格式（可选）

        Returns:
            用户信息列表
        """
        users = []
        all_notes = []
        total = len(user_urls)

        logger.info(f"Starting to crawl {total} users")

        for idx, user_url in enumerate(user_urls, 1):
            logger.info(f"[{idx}/{total}] Crawling user: {user_url}")

            try:
                result = self.crawl_user(
                    user_url,
                    fetch_notes=fetch_notes,
                    max_notes=max_notes,
                    export_format=None,  # 批量导出时不单独导出
                )

                if result:
                    users.append(result["user"])
                    if "notes" in result:
                        all_notes.extend(result["notes"])
                    logger.info(f"[{idx}/{total}] Successfully crawled user")
                else:
                    logger.warning(f"[{idx}/{total}] Failed to crawl user")

            except Exception as e:
                logger.error(f"[{idx}/{total}] Error crawling user: {e}")

        # 批量导出
        if export_format and users:
            from datetime import datetime

            # 导出用户信息
            filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = self.exporter.export_users(users, filename, export_format)
            logger.info(f"Exported {len(users)} users to {filepath}")

            # 导出笔记信息
            if all_notes:
                filename = f"users_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                filepath = self.exporter.export_notes(all_notes, filename, export_format)
                logger.info(f"Exported {len(all_notes)} notes to {filepath}")

        logger.info(f"Completed crawling {len(users)}/{total} users")
        return users
