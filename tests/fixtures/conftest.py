"""
测试Fixtures配置
提供可重用的测试数据和对象
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

# ============================================
# 配置相关Fixtures
# ============================================

@pytest.fixture
def temp_env_file(tmp_path):
    """创建临时环境变量文件"""
    env_file = tmp_path / ".env"
    env_content = """
XHS_COOKIES=test_cookie_value
RATE_LIMIT=3.0
RETRY_TIMES=3
TIMEOUT=30
"""
    env_file.write_text(env_content)
    return str(env_file)


@pytest.fixture
def invalid_env_file(tmp_path):
    """创建无效的环境变量文件（缺少必填项）"""
    env_file = tmp_path / ".env"
    env_content = """
RATE_LIMIT=3.0
"""
    env_file.write_text(env_content)
    return str(env_file)


@pytest.fixture
def mock_config():
    """模拟配置对象"""
    from src.core.config import SpiderConfig
    return SpiderConfig(
        cookies="test_cookie_value",
        rate_limit=3.0,
        retry_times=3,
        timeout=30,
        proxy=None
    )


# ============================================
# 数据相关Fixtures
# ============================================

@pytest.fixture
def sample_note_data() -> Dict[str, Any]:
    """示例笔记数据"""
    return {
        "note_id": "64a1b2c3d4e5f6g7h8i9j0k1",
        "note_url": "https://www.xiaohongshu.com/explore/64a1b2c3d4e5f6g7h8i9j0k1",
        "note_type": "图集",
        "title": "测试笔记标题",
        "desc": "这是一个测试笔记的描述内容",
        "user_id": "user123",
        "nickname": "测试用户",
        "liked_count": 100,
        "collected_count": 50,
        "comment_count": 20,
        "share_count": 10,
        "image_list": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ],
        "tags": ["测试", "示例"],
        "upload_time": "2024-01-01 12:00:00",
        "ip_location": "北京"
    }


@pytest.fixture
def sample_video_note_data() -> Dict[str, Any]:
    """示例视频笔记数据"""
    return {
        "note_id": "video123456789",
        "note_url": "https://www.xiaohongshu.com/explore/video123456789",
        "note_type": "视频",
        "title": "测试视频笔记",
        "desc": "这是一个测试视频笔记",
        "user_id": "user456",
        "nickname": "视频创作者",
        "liked_count": 200,
        "collected_count": 80,
        "comment_count": 30,
        "share_count": 15,
        "video_cover": "https://example.com/cover.jpg",
        "video_addr": "https://example.com/video.mp4",
        "image_list": [],
        "tags": ["视频", "测试"],
        "upload_time": "2024-01-02 15:30:00",
        "ip_location": "上海"
    }


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """示例用户数据"""
    return {
        "user_id": "user123",
        "nickname": "测试用户",
        "avatar": "https://example.com/avatar.jpg",
        "red_id": "test_red_id",
        "gender": "男",
        "ip_location": "北京",
        "desc": "这是用户简介",
        "follows": 100,
        "fans": 500,
        "interaction": 1000,
        "tags": ["美食", "旅行"]
    }


@pytest.fixture
def invalid_note_data() -> Dict[str, Any]:
    """无效的笔记数据（缺少必填字段）"""
    return {
        "note_id": "invalid123",
        "note_type": "未知类型",  # 无效的类型
        "title": "测试"
    }


# ============================================
# API响应Fixtures
# ============================================

@pytest.fixture
def mock_api_success_response() -> Dict[str, Any]:
    """模拟成功的API响应"""
    return {
        "success": True,
        "code": 0,
        "msg": "success",
        "data": {
            "items": [
                {
                    "id": "note123",
                    "note_card": {
                        "type": "normal",
                        "display_title": "测试笔记"
                    }
                }
            ]
        }
    }


@pytest.fixture
def mock_api_error_response() -> Dict[str, Any]:
    """模拟失败的API响应"""
    return {
        "success": False,
        "code": -1,
        "msg": "请求失败",
        "data": None
    }


# ============================================
# 文件系统Fixtures
# ============================================

@pytest.fixture
def temp_data_dir(tmp_path):
    """创建临时数据目录"""
    data_dir = tmp_path / "datas"
    data_dir.mkdir()
    (data_dir / "excel_datas").mkdir()
    (data_dir / "media_datas").mkdir()
    return str(data_dir)


@pytest.fixture
def temp_progress_file(tmp_path):
    """创建临时进度文件"""
    progress_file = tmp_path / ".progress.json"
    return str(progress_file)


@pytest.fixture
def temp_log_dir(tmp_path):
    """创建临时日志目录"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return str(log_dir)


# ============================================
# Mock对象Fixtures
# ============================================

@pytest.fixture
def mock_rate_limiter():
    """模拟速率限制器"""
    limiter = Mock()
    limiter.acquire = Mock()
    limiter.get_stats = Mock(return_value={"total_requests": 10, "limited_count": 2})
    return limiter


@pytest.fixture
def mock_error_handler():
    """模拟错误处理器"""
    handler = Mock()
    handler.handle_api_error = Mock()
    handler.handle_fatal_error = Mock()
    return handler


@pytest.fixture
def mock_logger():
    """模拟日志记录器"""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


# ============================================
# 测试数据集合Fixtures
# ============================================

@pytest.fixture
def sample_notes_list(sample_note_data, sample_video_note_data):
    """示例笔记列表"""
    return [sample_note_data, sample_video_note_data]


@pytest.fixture
def export_test_data():
    """用于导出测试的数据"""
    return [
        {
            "笔记ID": "note1",
            "标题": "测试笔记1",
            "点赞数": 100,
            "收藏数": 50
        },
        {
            "笔记ID": "note2",
            "标题": "测试笔记2",
            "点赞数": 200,
            "收藏数": 80
        }
    ]


# ============================================
# 清理Fixtures
# ============================================

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """自动清理临时文件"""
    yield
    # 测试后清理逻辑可以在这里添加
    pass
