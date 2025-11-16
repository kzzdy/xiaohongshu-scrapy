"""搜索爬虫模块"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from src.api.xhs_pc import XHSPCApi
from src.core.progress import ProgressManager
from src.data.processor import DataProcessor
from src.data.exporter import DataExporter, ExportFormat
from src.spider.note_spider import NoteSpider


class SearchSpider:
    """搜索爬虫

    负责搜索小红书笔记，支持：
    - 关键词搜索
    - 多种排序和筛选选项
    - 进度管理
    - 数据导出
    """

    # 排序方式
    SORT_GENERAL = 0  # 综合
    SORT_TIME = 1  # 最新
    SORT_POPULARITY = 2  # 最多点赞
    SORT_COMMENT = 3  # 最多评论
    SORT_COLLECT = 4  # 最多收藏

    # 笔记类型
    NOTE_TYPE_ALL = 0  # 不限
    NOTE_TYPE_VIDEO = 1  # 视频笔记
    NOTE_TYPE_NORMAL = 2  # 普通笔记

    # 笔记时间
    NOTE_TIME_ALL = 0  # 不限
    NOTE_TIME_DAY = 1  # 一天内
    NOTE_TIME_WEEK = 2  # 一周内
    NOTE_TIME_HALF_YEAR = 3  # 半年内

    def __init__(
        self,
        api_client: XHSPCApi,
        progress_manager: Optional[ProgressManager] = None,
        data_processor: Optional[DataProcessor] = None,
        data_exporter: Optional[DataExporter] = None,
        note_spider: Optional[NoteSpider] = None,
    ):
        """初始化搜索爬虫

        Args:
            api_client: 小红书PC端API客户端
            progress_manager: 进度管理器（可选）
            data_processor: 数据处理器（可选）
            data_exporter: 数据导出器（可选）
            note_spider: 笔记爬虫（可选，用于下载媒体文件）
        """
        self.api = api_client
        self.progress = progress_manager or ProgressManager()
        self.processor = data_processor or DataProcessor()
        self.exporter = data_exporter or DataExporter()
        self.note_spider = note_spider

    def search_notes(
        self,
        query: str,
        num: int = 20,
        sort_type: int = SORT_GENERAL,
        note_type: int = NOTE_TYPE_ALL,
        note_time: int = NOTE_TIME_ALL,
    ) -> List[Dict[str, Any]]:
        """搜索笔记

        Args:
            query: 搜索关键词
            num: 需要的笔记数量
            sort_type: 排序方式（0:综合, 1:最新, 2:最多点赞, 3:最多评论, 4:最多收藏）
            note_type: 笔记类型（0:不限, 1:视频笔记, 2:普通笔记）
            note_time: 笔记时间（0:不限, 1:一天内, 2:一周内, 3:半年内）

        Returns:
            笔记信息列表
        """
        logger.info(f"Searching notes: query='{query}', num={num}, sort={sort_type}")

        # 调用API搜索笔记
        success, msg, note_list = self.api.search_some_note(
            query=query,
            require_num=num,
            sort_type_choice=sort_type,
            note_type=note_type,
            note_time=note_time,
        )

        if not success:
            logger.error(f"Failed to search notes: {msg}")
            return []

        logger.info(f"Found {len(note_list)} notes")

        # 过滤出笔记（排除其他类型如广告）
        note_list = [n for n in note_list if n.get('model_type') == 'note']
        logger.info(f"Filtered to {len(note_list)} actual notes")

        # 搜索结果只有简单信息，需要逐个获取详细信息
        processed_notes = []
        for idx, note_data in enumerate(note_list, 1):
            try:
                # 构建笔记 URL
                note_id = note_data.get('id', '')
                xsec_token = note_data.get('xsec_token', '')
                note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
                if xsec_token:
                    note_url += f"?xsec_token={xsec_token}"

                logger.debug(f"[{idx}/{len(note_list)}] Fetching note details: {note_url}")

                # 使用 note_spider 获取详细信息
                note_info = self.note_spider.fetch_note(note_url)

                if note_info:
                    processed_notes.append(note_info)
                    logger.debug(
                        f"[{idx}/{len(note_list)}] Processed note: {note_info['note_id']}"
                    )
                else:
                    logger.warning(f"[{idx}/{len(note_list)}] Failed to fetch note details")

            except Exception as e:
                logger.error(f"[{idx}/{len(note_list)}] Error processing note: {e}")

        logger.info(f"Successfully processed {len(processed_notes)}/{len(note_list)} notes")
        return processed_notes

    def _convert_search_note_to_full_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """将搜索笔记数据转换为完整笔记数据格式

        Args:
            note_data: 搜索笔记数据

        Returns:
            完整笔记数据格式
        """
        # 搜索结果中的笔记数据已经是比较完整的格式
        # 但需要确保字段名称和结构符合处理器的要求
        note_id = note_data.get("id", "")
        
        # 构建笔记 URL
        xsec_token = note_data.get("xsec_token", "")
        note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
        if xsec_token:
            note_url += f"?xsec_token={xsec_token}"

        # 如果已经有note_card字段，添加url后返回
        if "note_card" in note_data:
            note_data["url"] = note_url
            return note_data

        # 否则构建标准格式
        # 搜索结果的数据结构和笔记详情不同，需要转换
        full_note = {
            "id": note_id,
            "url": note_url,
            "note_card": note_data,  # 将整个搜索结果作为note_card
        }

        return full_note

    def search_users(
        self,
        query: str,
        num: int = 15,
    ) -> List[Dict[str, Any]]:
        """搜索用户

        Args:
            query: 搜索关键词
            num: 需要的用户数量

        Returns:
            用户信息列表
        """
        logger.info(f"Searching users: query='{query}', num={num}")

        # 调用API搜索用户
        success, msg, user_list = self.api.search_some_user(
            query=query,
            require_num=num,
        )

        if not success:
            logger.error(f"Failed to search users: {msg}")
            return []

        logger.info(f"Found {len(user_list)} users")

        # 处理用户数据
        processed_users = []
        for idx, user_data in enumerate(user_list, 1):
            try:
                # 提取用户ID
                user_id = user_data.get("user_id", "")

                # 构建用户信息（搜索结果是简化版，需要转换）
                user_info = self._convert_search_user_to_user_info(user_data)

                if user_info:
                    processed_users.append(user_info)
                    logger.debug(
                        f"[{idx}/{len(user_list)}] Processed user: {user_info['nickname']}"
                    )
                else:
                    logger.warning(f"[{idx}/{len(user_list)}] Failed to process user")

            except Exception as e:
                logger.error(f"[{idx}/{len(user_list)}] Error processing user: {e}")

        logger.info(f"Successfully processed {len(processed_users)}/{len(user_list)} users")
        return processed_users

    def _convert_search_user_to_user_info(
        self, user_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """将搜索用户数据转换为用户信息格式

        Args:
            user_data: 搜索用户数据

        Returns:
            用户信息字典
        """
        try:
            user_id = user_data.get("user_id", "")

            user_info = {
                "user_id": user_id,
                "home_url": f"https://www.xiaohongshu.com/user/profile/{user_id}",
                "nickname": user_data.get("nickname", ""),
                "avatar": user_data.get("avatar", ""),
                "red_id": user_data.get("red_id", ""),
                "gender": "未知",  # 搜索结果中通常没有性别信息
                "ip_location": user_data.get("ip_location", "未知"),
                "desc": user_data.get("desc", ""),
                "follows": user_data.get("follows", 0),
                "fans": user_data.get("fans", 0),
                "interaction": user_data.get("interaction", 0),
                "tags": [],  # 搜索结果中通常没有标签信息
            }

            return user_info

        except Exception as e:
            logger.error(f"Error converting search user data: {e}")
            return None

    def crawl_search_notes(
        self,
        query: str,
        num: int = 20,
        sort_type: int = SORT_GENERAL,
        note_type: int = NOTE_TYPE_ALL,
        note_time: int = NOTE_TIME_ALL,
        save_media: bool = False,
        export_format: Optional[ExportFormat] = None,
        use_progress: bool = False,
    ) -> List[Dict[str, Any]]:
        """搜索并爬取笔记（完整流程）

        Args:
            query: 搜索关键词
            num: 需要的笔记数量
            sort_type: 排序方式
            note_type: 笔记类型
            note_time: 笔记时间
            save_media: 是否保存媒体文件
            export_format: 导出格式（可选）
            use_progress: 是否使用进度管理

        Returns:
            笔记信息列表
        """
        # 搜索笔记
        notes = self.search_notes(
            query=query,
            num=num,
            sort_type=sort_type,
            note_type=note_type,
            note_time=note_time,
        )

        if not notes:
            logger.warning("No notes found")
            return []

        # 过滤已完成的笔记
        if use_progress:
            original_count = len(notes)
            notes = [note for note in notes if not self.progress.is_completed(note["note_id"])]
            logger.info(
                f"Filtered {original_count - len(notes)} completed notes, {len(notes)} remaining"
            )

        # 下载媒体文件
        if save_media and self.note_spider:
            logger.info(f"Downloading media files for {len(notes)} notes")
            for idx, note in enumerate(notes, 1):
                try:
                    self.note_spider.download_media(note)

                    # 标记为已完成
                    if use_progress:
                        self.progress.mark_completed(note["note_id"])

                    logger.info(f"[{idx}/{len(notes)}] Downloaded media for note {note['note_id']}")

                except Exception as e:
                    logger.error(
                        f"[{idx}/{len(notes)}] Failed to download media for note {note['note_id']}: {e}"
                    )

        # 导出数据
        if export_format:
            filename = f"search_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = self.exporter.export_notes(notes, filename, export_format)
            logger.info(f"Exported {len(notes)} notes to {filepath}")

        return notes

    def crawl_search_users(
        self,
        query: str,
        num: int = 15,
        export_format: Optional[ExportFormat] = None,
    ) -> List[Dict[str, Any]]:
        """搜索并爬取用户（完整流程）

        Args:
            query: 搜索关键词
            num: 需要的用户数量
            export_format: 导出格式（可选）

        Returns:
            用户信息列表
        """
        # 搜索用户
        users = self.search_users(query=query, num=num)

        if not users:
            logger.warning("No users found")
            return []

        # 导出数据
        if export_format:
            filename = f"search_users_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = self.exporter.export_users(users, filename, export_format)
            logger.info(f"Exported {len(users)} users to {filepath}")

        return users

    def get_search_recommendations(self, keyword: str) -> List[str]:
        """获取搜索关键词推荐

        Args:
            keyword: 搜索关键词

        Returns:
            推荐关键词列表
        """
        logger.info(f"Getting search recommendations for: {keyword}")

        success, msg, res_json = self.api.get_search_keyword(keyword)

        if not success:
            logger.error(f"Failed to get search recommendations: {msg}")
            return []

        # 提取推荐关键词
        recommendations = []
        try:
            items = res_json.get("data", {}).get("items", [])
            for item in items:
                keyword_text = item.get("keyword", "")
                if keyword_text:
                    recommendations.append(keyword_text)
        except Exception as e:
            logger.error(f"Error parsing search recommendations: {e}")

        logger.info(f"Found {len(recommendations)} recommendations")
        return recommendations

    def get_progress_stats(self) -> Dict[str, Any]:
        """获取进度统计信息

        Returns:
            进度统计信息字典
        """
        return self.progress.get_stats()

    def clear_progress(self) -> None:
        """清除进度记录"""
        self.progress.clear_progress()
        logger.info("Progress cleared")
