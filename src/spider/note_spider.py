"""笔记爬虫模块"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from loguru import logger

from src.api.xhs_pc import XHSPCApi
from src.core.progress import ProgressManager
from src.data.processor import DataProcessor
from src.data.exporter import DataExporter, ExportFormat
from src.data.validator import DataValidator


class NoteSpider:
    """笔记爬虫

    负责爬取小红书笔记信息，支持：
    - 单个笔记爬取
    - 批量笔记爬取
    - 断点续传
    - 媒体文件下载
    """

    def __init__(
        self,
        api_client: XHSPCApi,
        progress_manager: Optional[ProgressManager] = None,
        data_processor: Optional[DataProcessor] = None,
        data_exporter: Optional[DataExporter] = None,
        media_dir: str = "datas/media_datas",
    ):
        """初始化笔记爬虫

        Args:
            api_client: 小红书PC端API客户端
            progress_manager: 进度管理器（可选）
            data_processor: 数据处理器（可选）
            data_exporter: 数据导出器（可选）
            media_dir: 媒体文件保存目录
        """
        self.api = api_client
        self.progress = progress_manager or ProgressManager()
        self.processor = data_processor or DataProcessor()
        self.exporter = data_exporter or DataExporter()
        self.validator = DataValidator()
        self.media_dir = Path(media_dir)
        self.media_dir.mkdir(parents=True, exist_ok=True)

    def fetch_note(self, note_url: str) -> Optional[Dict[str, Any]]:
        """获取单个笔记信息

        Args:
            note_url: 笔记URL

        Returns:
            处理后的笔记信息字典，失败返回None
        """
        logger.info(f"Fetching note: {note_url}")

        # 调用API获取笔记信息
        success, msg, res_json = self.api.get_note_info(note_url)

        if not success:
            logger.error(f"Failed to fetch note: {msg}")
            return None

        # 检查响应数据
        if not res_json or "data" not in res_json:
            logger.error("Invalid response data")
            return None

        # 获取笔记数据
        items = res_json.get("data", {}).get("items", [])
        if not items:
            logger.error("No note data found in response")
            return None

        # 处理笔记数据
        note_data = items[0]
        
        # 添加 URL 字段（API 返回的数据中没有这个字段）
        note_data['url'] = note_url
        
        processed_note = self.processor.handle_note_info(note_data)

        if not processed_note:
            logger.error("Failed to process note data")
            return None

        logger.info(f"Successfully fetched note: {processed_note['note_id']}")
        return processed_note

    def fetch_notes(
        self,
        note_urls: List[str],
        use_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """批量获取笔记信息

        Args:
            note_urls: 笔记URL列表
            use_progress: 是否使用进度管理（断点续传）

        Returns:
            处理后的笔记信息列表
        """
        notes = []
        total = len(note_urls)

        logger.info(f"Starting to fetch {total} notes")

        for idx, note_url in enumerate(note_urls, 1):
            # 从URL中提取笔记ID
            try:
                note_id = note_url.split("/")[-1].split("?")[0]
            except Exception as e:
                logger.warning(f"Failed to extract note_id from URL: {note_url}")
                continue

            # 检查是否已完成
            if use_progress and self.progress.is_completed(note_id):
                logger.info(f"[{idx}/{total}] Note {note_id} already completed, skipping")
                continue

            # 获取笔记信息
            note = self.fetch_note(note_url)

            if note:
                notes.append(note)

                # 标记为已完成
                if use_progress:
                    self.progress.mark_completed(note_id)

                logger.info(f"[{idx}/{total}] Successfully fetched note {note_id}")
            else:
                logger.warning(f"[{idx}/{total}] Failed to fetch note from {note_url}")

        logger.info(f"Completed fetching {len(notes)}/{total} notes")
        return notes

    def download_media(
        self,
        note: Dict[str, Any],
        save_images: bool = True,
        save_video: bool = True,
    ) -> Dict[str, List[str]]:
        """下载笔记的媒体文件

        Args:
            note: 笔记信息字典
            save_images: 是否保存图片
            save_video: 是否保存视频

        Returns:
            下载结果字典，包含成功下载的文件路径列表
        """
        result = {"images": [], "video": []}

        note_id = note["note_id"]
        note_type = note["note_type"]
        title = self.validator.clean_filename(note["title"])

        # 创建笔记目录
        note_dir = self.media_dir / f"{title}_{note_id}"
        note_dir.mkdir(parents=True, exist_ok=True)

        # 保存笔记详情
        self.processor.save_note_detail(note, str(note_dir))

        # 下载图片
        if save_images and note["image_list"]:
            logger.info(f"Downloading {len(note['image_list'])} images for note {note_id}")

            for idx, image_url in enumerate(note["image_list"], 1):
                try:
                    image_path = note_dir / f"image_{idx}.jpg"

                    # 检查文件是否已存在
                    if image_path.exists():
                        logger.debug(f"Image already exists: {image_path}")
                        result["images"].append(str(image_path))
                        continue

                    # 下载图片
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()

                    with open(image_path, "wb") as f:
                        f.write(response.content)

                    result["images"].append(str(image_path))
                    logger.debug(f"Downloaded image {idx}/{len(note['image_list'])}: {image_path}")

                except Exception as e:
                    logger.error(f"Failed to download image {idx}: {e}")

        # 下载视频
        if save_video and note_type == "视频" and note.get("video_addr"):
            logger.info(f"Downloading video for note {note_id}")

            try:
                video_path = note_dir / "video.mp4"

                # 检查文件是否已存在
                if video_path.exists():
                    logger.debug(f"Video already exists: {video_path}")
                    result["video"].append(str(video_path))
                else:
                    # 下载视频
                    response = requests.get(note["video_addr"], timeout=60, stream=True)
                    response.raise_for_status()

                    with open(video_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    result["video"].append(str(video_path))
                    logger.info(f"Downloaded video: {video_path}")

            except Exception as e:
                logger.error(f"Failed to download video: {e}")

        return result

    def crawl_note(
        self,
        note_url: str,
        save_media: bool = False,
        export_format: Optional[ExportFormat] = None,
    ) -> Optional[Dict[str, Any]]:
        """爬取单个笔记（完整流程）

        Args:
            note_url: 笔记URL
            save_media: 是否保存媒体文件
            export_format: 导出格式（可选）

        Returns:
            笔记信息字典，失败返回None
        """
        # 获取笔记信息
        note = self.fetch_note(note_url)

        if not note:
            return None

        # 下载媒体文件
        if save_media:
            media_result = self.download_media(note)
            logger.info(
                f"Downloaded {len(media_result['images'])} images and {len(media_result['video'])} videos"
            )

        # 导出数据
        if export_format:
            filename = f"note_{note['note_id']}"
            self.exporter.export_notes([note], filename, export_format)

        return note

    def crawl_notes(
        self,
        note_urls: List[str],
        save_media: bool = False,
        export_format: Optional[ExportFormat] = None,
        use_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """批量爬取笔记（完整流程）

        Args:
            note_urls: 笔记URL列表
            save_media: 是否保存媒体文件
            export_format: 导出格式（可选）
            use_progress: 是否使用断点续传

        Returns:
            笔记信息列表
        """
        # 获取笔记信息
        notes = self.fetch_notes(note_urls, use_progress)

        if not notes:
            logger.warning("No notes fetched")
            return []

        # 下载媒体文件
        if save_media:
            logger.info(f"Downloading media files for {len(notes)} notes")
            for note in notes:
                try:
                    self.download_media(note)
                except Exception as e:
                    logger.error(f"Failed to download media for note {note['note_id']}: {e}")

        # 导出数据
        if export_format:
            from datetime import datetime

            filename = f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = self.exporter.export_notes(notes, filename, export_format)
            logger.info(f"Exported {len(notes)} notes to {filepath}")

        return notes

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
