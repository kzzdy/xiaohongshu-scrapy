"""
测试环境配置验证
验证测试环境是否正确配置
"""

import pytest
from pathlib import Path


def test_pytest_working():
    """验证pytest正常工作"""
    assert True


def test_fixtures_available(sample_note_data, sample_user_data):
    """验证fixtures可用"""
    assert sample_note_data is not None
    assert sample_user_data is not None
    assert "note_id" in sample_note_data
    assert "user_id" in sample_user_data


def test_temp_directories(temp_data_dir, temp_log_dir):
    """验证临时目录创建"""
    assert Path(temp_data_dir).exists()
    assert Path(temp_log_dir).exists()


def test_mock_responses_file_exists():
    """验证mock响应文件存在"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    mock_file = fixtures_dir / "mock_responses.json"
    assert mock_file.exists()


def test_test_data_file_exists():
    """验证测试数据文件存在"""
    fixtures_dir = Path(__file__).parent / "fixtures"
    data_file = fixtures_dir / "test_data.json"
    assert data_file.exists()


def test_helpers_module_import():
    """验证辅助工具模块可导入"""
    from tests.fixtures import helpers
    assert hasattr(helpers, 'load_mock_response')
    assert hasattr(helpers, 'load_test_data')
    assert hasattr(helpers, 'create_mock_response')


def test_load_mock_response():
    """验证加载mock响应功能"""
    from tests.fixtures.helpers import load_mock_response
    
    response = load_mock_response('note_detail_success')
    assert response is not None
    assert 'success' in response
    assert response['success'] is True


def test_load_test_data():
    """验证加载测试数据功能"""
    from tests.fixtures.helpers import load_test_data
    
    keywords = load_test_data('search_keywords')
    assert keywords is not None
    assert isinstance(keywords, list)
    assert len(keywords) > 0


@pytest.mark.unit
def test_unit_marker():
    """验证unit标记可用"""
    assert True


@pytest.mark.integration
def test_integration_marker():
    """验证integration标记可用"""
    assert True


def test_mock_config_fixture(mock_config):
    """验证配置fixture"""
    assert mock_config is not None
    assert hasattr(mock_config, 'cookies')
    assert hasattr(mock_config, 'rate_limit')
    assert mock_config.rate_limit == 3.0


def test_mock_rate_limiter_fixture(mock_rate_limiter):
    """验证速率限制器fixture"""
    assert mock_rate_limiter is not None
    mock_rate_limiter.acquire()
    stats = mock_rate_limiter.get_stats()
    assert 'total_requests' in stats


def test_export_test_data_fixture(export_test_data):
    """验证导出测试数据fixture"""
    assert export_test_data is not None
    assert isinstance(export_test_data, list)
    assert len(export_test_data) > 0
    assert "笔记ID" in export_test_data[0]
