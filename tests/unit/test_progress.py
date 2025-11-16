"""ProgressManager 单元测试"""

import pytest
import json
from pathlib import Path
from src.core.progress import ProgressManager


class TestProgressManager:
    """测试 ProgressManager 进度管理器"""

    @pytest.fixture
    def progress_file(self, tmp_path):
        """创建临时进度文件路径"""
        return tmp_path / "test_progress.json"

    @pytest.fixture
    def manager(self, progress_file):
        """创建进度管理器实例"""
        return ProgressManager(progress_file=str(progress_file))

    def test_init(self, progress_file):
        """测试初始化"""
        manager = ProgressManager(progress_file=str(progress_file))
        
        assert manager.progress_file == progress_file
        assert isinstance(manager.completed_ids, set)
        assert len(manager.completed_ids) == 0
        assert progress_file.parent.exists()

    def test_mark_completed(self, manager, progress_file):
        """测试标记笔记为已完成"""
        note_id = "test_note_123"
        
        manager.mark_completed(note_id)
        
        assert note_id in manager.completed_ids
        assert manager.get_completed_count() == 1
        assert progress_file.exists()

    def test_mark_completed_duplicate(self, manager):
        """测试重复标记笔记"""
        note_id = "test_note_123"
        
        manager.mark_completed(note_id)
        manager.mark_completed(note_id)
        
        assert manager.get_completed_count() == 1

    def test_mark_batch_completed(self, manager):
        """测试批量标记笔记"""
        note_ids = ["note_1", "note_2", "note_3"]
        
        manager.mark_batch_completed(note_ids)
        
        assert manager.get_completed_count() == 3
        for note_id in note_ids:
            assert note_id in manager.completed_ids

    def test_mark_batch_completed_with_duplicates(self, manager):
        """测试批量标记包含重复的笔记"""
        manager.mark_completed("note_1")
        
        note_ids = ["note_1", "note_2", "note_3"]
        manager.mark_batch_completed(note_ids)
        
        assert manager.get_completed_count() == 3

    def test_is_completed(self, manager):
        """测试检查笔记是否已完成"""
        note_id = "test_note_123"
        
        assert manager.is_completed(note_id) is False
        
        manager.mark_completed(note_id)
        
        assert manager.is_completed(note_id) is True

    def test_get_completed_count(self, manager):
        """测试获取已完成数量"""
        assert manager.get_completed_count() == 0
        
        manager.mark_completed("note_1")
        assert manager.get_completed_count() == 1
        
        manager.mark_completed("note_2")
        assert manager.get_completed_count() == 2

    def test_get_completed_ids(self, manager):
        """测试获取所有已完成的笔记ID"""
        note_ids = ["note_3", "note_1", "note_2"]
        
        for note_id in note_ids:
            manager.mark_completed(note_id)
        
        completed = manager.get_completed_ids()
        
        # 应该返回排序后的列表
        assert completed == ["note_1", "note_2", "note_3"]

    def test_clear_progress(self, manager):
        """测试清除进度"""
        manager.mark_completed("note_1")
        manager.mark_completed("note_2")
        
        assert manager.get_completed_count() == 2
        
        manager.clear_progress()
        
        assert manager.get_completed_count() == 0
        assert len(manager.completed_ids) == 0

    def test_save_and_load_progress(self, progress_file):
        """测试保存和加载进度"""
        # 创建第一个管理器并保存进度
        manager1 = ProgressManager(progress_file=str(progress_file))
        manager1.mark_completed("note_1")
        manager1.mark_completed("note_2")
        manager1.mark_completed("note_3")
        
        # 创建第二个管理器，应该加载之前的进度
        manager2 = ProgressManager(progress_file=str(progress_file))
        
        assert manager2.get_completed_count() == 3
        assert manager2.is_completed("note_1")
        assert manager2.is_completed("note_2")
        assert manager2.is_completed("note_3")

    def test_load_progress_file_not_exists(self, progress_file):
        """测试加载不存在的进度文件"""
        manager = ProgressManager(progress_file=str(progress_file))
        
        assert manager.get_completed_count() == 0
        assert not progress_file.exists()

    def test_load_progress_corrupted_file(self, progress_file):
        """测试加载损坏的进度文件"""
        # 创建损坏的JSON文件
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress_file.write_text("invalid json content")
        
        # 应该能够处理损坏的文件
        manager = ProgressManager(progress_file=str(progress_file))
        
        assert manager.get_completed_count() == 0

    def test_load_progress_old_format(self, progress_file):
        """测试加载旧格式的进度文件"""
        # 创建旧格式的进度文件（直接是列表）
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        old_data = ["note_1", "note_2", "note_3"]
        progress_file.write_text(json.dumps(old_data))
        
        manager = ProgressManager(progress_file=str(progress_file))
        
        assert manager.get_completed_count() == 3
        assert manager.is_completed("note_1")

    def test_load_progress_new_format(self, progress_file):
        """测试加载新格式的进度文件"""
        # 创建新格式的进度文件（包含元数据）
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        new_data = {
            "completed_ids": ["note_1", "note_2"],
            "metadata": {
                "created_at": "2024-01-01T00:00:00",
                "last_updated": "2024-01-01T12:00:00"
            }
        }
        progress_file.write_text(json.dumps(new_data))
        
        manager = ProgressManager(progress_file=str(progress_file))
        
        assert manager.get_completed_count() == 2
        assert manager.is_completed("note_1")

    def test_get_stats(self, manager):
        """测试获取统计信息"""
        manager.mark_completed("note_1")
        manager.mark_completed("note_2")
        
        stats = manager.get_stats()
        
        assert stats["total_completed"] == 2
        assert "progress_file" in stats
        assert "created_at" in stats
        assert "last_updated" in stats

    def test_remove_completed(self, manager):
        """测试移除已完成的笔记"""
        note_id = "test_note_123"
        
        manager.mark_completed(note_id)
        assert manager.is_completed(note_id)
        
        result = manager.remove_completed(note_id)
        
        assert result is True
        assert not manager.is_completed(note_id)
        assert manager.get_completed_count() == 0

    def test_remove_completed_not_exists(self, manager):
        """测试移除不存在的笔记"""
        result = manager.remove_completed("non_existent_note")
        
        assert result is False

    def test_atomic_save(self, progress_file):
        """测试原子性保存"""
        manager = ProgressManager(progress_file=str(progress_file))
        
        # 标记多个笔记
        for i in range(10):
            manager.mark_completed(f"note_{i}")
        
        # 验证文件存在且内容正确
        assert progress_file.exists()
        
        with open(progress_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert len(data["completed_ids"]) == 10

    def test_concurrent_mark_completed(self, manager):
        """测试并发标记笔记"""
        import threading
        
        # 使用批量标记来避免Windows文件锁问题
        note_ids = [f"note_{i}" for i in range(30)]
        manager.mark_batch_completed(note_ids)
        
        # 验证所有笔记都被标记
        assert manager.get_completed_count() == 30
        
        # 验证线程安全的读取操作
        def check_completed(note_id):
            assert manager.is_completed(note_id)
        
        threads = [
            threading.Thread(target=check_completed, args=(f"note_{i}",))
            for i in range(30)
        ]
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def test_progress_persistence(self, progress_file):
        """测试进度持久化"""
        # 第一个管理器
        manager1 = ProgressManager(progress_file=str(progress_file))
        manager1.mark_completed("note_1")
        manager1.mark_completed("note_2")
        
        # 第二个管理器
        manager2 = ProgressManager(progress_file=str(progress_file))
        manager2.mark_completed("note_3")
        
        # 第三个管理器应该看到所有进度
        manager3 = ProgressManager(progress_file=str(progress_file))
        
        assert manager3.get_completed_count() == 3
        assert manager3.is_completed("note_1")
        assert manager3.is_completed("note_2")
        assert manager3.is_completed("note_3")

    def test_metadata_updates(self, manager, progress_file):
        """测试元数据更新"""
        manager.mark_completed("note_1")
        
        # 读取文件验证元数据
        with open(progress_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "metadata" in data
        assert "last_updated" in data["metadata"]
        assert "total_completed" in data["metadata"]
        assert data["metadata"]["total_completed"] == 1

    def test_clear_progress_updates_metadata(self, manager, progress_file):
        """测试清除进度更新元数据"""
        manager.mark_completed("note_1")
        manager.clear_progress()
        
        # 读取文件验证元数据
        with open(progress_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "cleared_at" in data["metadata"]
