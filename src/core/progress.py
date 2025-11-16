"""进度管理器模块"""

from typing import Set, List, Dict, Any
import json
from pathlib import Path
from threading import Lock
from datetime import datetime


class ProgressManager:
    """进度管理器

    管理下载进度，支持断点续传功能。
    使用JSON文件持久化已完成的笔记ID，避免重复下载。
    """

    def __init__(self, progress_file: str = "datas/.progress.json"):
        """初始化进度管理器

        Args:
            progress_file: 进度文件路径，默认为datas/.progress.json
        """
        self.progress_file = Path(progress_file)
        self.completed_ids: Set[str] = set()
        self.lock = Lock()
        self._metadata: Dict[str, Any] = {}

        # 确保进度文件目录存在
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        # 加载已有进度
        self.load_progress()

    def load_progress(self) -> None:
        """加载进度

        从JSON文件中加载已完成的笔记ID列表。
        如果文件不存在或格式错误，将创建新的进度记录。
        """
        with self.lock:
            if not self.progress_file.exists():
                self.completed_ids = set()
                self._metadata = {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                }
                return

            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 兼容旧格式（直接是列表）和新格式（包含元数据）
                if isinstance(data, list):
                    self.completed_ids = set(data)
                    self._metadata = {
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                    }
                elif isinstance(data, dict):
                    self.completed_ids = set(data.get("completed_ids", []))
                    self._metadata = data.get("metadata", {})
                else:
                    raise ValueError("无效的进度文件格式")

            except (json.JSONDecodeError, ValueError) as e:
                # 文件损坏，创建新的进度记录
                self.completed_ids = set()
                self._metadata = {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "error": f"原进度文件损坏: {str(e)}",
                }

    def save_progress(self) -> None:
        """保存进度

        将当前进度原子性地写入JSON文件。
        使用临时文件+重命名的方式确保写入的原子性，防止数据损坏。
        """
        # 更新元数据
        self._metadata["last_updated"] = datetime.now().isoformat()
        self._metadata["total_completed"] = len(self.completed_ids)

        # 准备数据
        data = {
            "completed_ids": sorted(list(self.completed_ids)),
            "metadata": self._metadata,
        }

        # 使用临时文件确保原子性写入
        temp_file = self.progress_file.with_suffix(".tmp")

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 原子性替换
            temp_file.replace(self.progress_file)

        except Exception as e:
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()
            raise e

    def mark_completed(self, note_id: str) -> None:
        """标记笔记为已完成

        Args:
            note_id: 笔记ID
        """
        with self.lock:
            if note_id not in self.completed_ids:
                self.completed_ids.add(note_id)
        # 在锁外保存进度
        self.save_progress()

    def mark_batch_completed(self, note_ids: List[str]) -> None:
        """批量标记笔记为已完成

        Args:
            note_ids: 笔记ID列表
        """
        should_save = False
        with self.lock:
            original_count = len(self.completed_ids)
            self.completed_ids.update(note_ids)

            # 只有在有新增时才保存
            if len(self.completed_ids) > original_count:
                should_save = True

        if should_save:
            self.save_progress()

    def is_completed(self, note_id: str) -> bool:
        """检查笔记是否已完成

        Args:
            note_id: 笔记ID

        Returns:
            bool: 如果笔记已完成返回True，否则返回False
        """
        with self.lock:
            return note_id in self.completed_ids

    def get_completed_count(self) -> int:
        """获取已完成数量

        Returns:
            int: 已完成的笔记数量
        """
        with self.lock:
            return len(self.completed_ids)

    def get_completed_ids(self) -> List[str]:
        """获取所有已完成的笔记ID

        Returns:
            List[str]: 已完成的笔记ID列表
        """
        with self.lock:
            return sorted(list(self.completed_ids))

    def clear_progress(self) -> None:
        """清除进度

        清空所有已完成的笔记记录，并更新元数据。
        """
        with self.lock:
            self.completed_ids.clear()
            self._metadata["cleared_at"] = datetime.now().isoformat()
        self.save_progress()

    def get_stats(self) -> Dict[str, Any]:
        """获取进度统计信息

        Returns:
            Dict[str, Any]: 包含统计信息的字典
        """
        with self.lock:
            return {
                "total_completed": len(self.completed_ids),
                "progress_file": str(self.progress_file),
                "created_at": self._metadata.get("created_at", "未知"),
                "last_updated": self._metadata.get("last_updated", "未知"),
            }

    def remove_completed(self, note_id: str) -> bool:
        """从已完成列表中移除笔记

        Args:
            note_id: 笔记ID

        Returns:
            bool: 如果成功移除返回True，如果笔记不在列表中返回False
        """
        removed = False
        with self.lock:
            if note_id in self.completed_ids:
                self.completed_ids.remove(note_id)
                removed = True

        if removed:
            self.save_progress()
        return removed
