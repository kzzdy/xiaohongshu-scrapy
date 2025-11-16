"""
测试辅助工具函数
提供测试中常用的工具方法
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock
import tempfile
import shutil


def load_mock_response(response_name: str) -> Dict[str, Any]:
    """
    加载模拟API响应数据
    
    Args:
        response_name: 响应名称（在mock_responses.json中定义）
        
    Returns:
        模拟响应数据字典
    """
    fixtures_dir = Path(__file__).parent
    mock_file = fixtures_dir / "mock_responses.json"
    
    with open(mock_file, 'r', encoding='utf-8') as f:
        responses = json.load(f)
    
    return responses.get(response_name, {})


def load_test_data(data_key: str) -> Any:
    """
    加载测试数据
    
    Args:
        data_key: 数据键名（在test_data.json中定义）
        
    Returns:
        测试数据
    """
    fixtures_dir = Path(__file__).parent
    data_file = fixtures_dir / "test_data.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    return test_data.get(data_key)


def create_temp_directory() -> str:
    """
    创建临时目录
    
    Returns:
        临时目录路径
    """
    return tempfile.mkdtemp()


def cleanup_temp_directory(temp_dir: str) -> None:
    """
    清理临时目录
    
    Args:
        temp_dir: 临时目录路径
    """
    if Path(temp_dir).exists():
        shutil.rmtree(temp_dir)


def create_mock_response(status_code: int = 200, json_data: Dict = None, text: str = None):
    """
    创建模拟HTTP响应对象
    
    Args:
        status_code: HTTP状态码
        json_data: JSON响应数据
        text: 文本响应数据
        
    Returns:
        模拟响应对象
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.ok = 200 <= status_code < 300
    
    if json_data is not None:
        mock_response.json.return_value = json_data
    
    if text is not None:
        mock_response.text = text
    
    mock_response.headers = {}
    mock_response.raise_for_status = Mock()
    
    if not mock_response.ok:
        from requests.exceptions import HTTPError
        mock_response.raise_for_status.side_effect = HTTPError()
    
    return mock_response


def assert_file_exists(filepath: str) -> bool:
    """
    断言文件存在
    
    Args:
        filepath: 文件路径
        
    Returns:
        文件是否存在
    """
    return Path(filepath).exists()


def assert_file_not_empty(filepath: str) -> bool:
    """
    断言文件不为空
    
    Args:
        filepath: 文件路径
        
    Returns:
        文件是否不为空
    """
    path = Path(filepath)
    return path.exists() and path.stat().st_size > 0


def create_test_file(directory: str, filename: str, content: str = "") -> str:
    """
    创建测试文件
    
    Args:
        directory: 目录路径
        filename: 文件名
        content: 文件内容
        
    Returns:
        文件完整路径
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    file_path = dir_path / filename
    file_path.write_text(content, encoding='utf-8')
    
    return str(file_path)


def count_files_in_directory(directory: str, pattern: str = "*") -> int:
    """
    统计目录中的文件数量
    
    Args:
        directory: 目录路径
        pattern: 文件匹配模式
        
    Returns:
        文件数量
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return 0
    
    return len(list(dir_path.glob(pattern)))


def read_json_file(filepath: str) -> Dict[str, Any]:
    """
    读取JSON文件
    
    Args:
        filepath: 文件路径
        
    Returns:
        JSON数据字典
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file(filepath: str, data: Dict[str, Any]) -> None:
    """
    写入JSON文件
    
    Args:
        filepath: 文件路径
        data: 要写入的数据
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compare_dicts(dict1: Dict, dict2: Dict, ignore_keys: List[str] = None) -> bool:
    """
    比较两个字典是否相等（可忽略某些键）
    
    Args:
        dict1: 字典1
        dict2: 字典2
        ignore_keys: 要忽略的键列表
        
    Returns:
        是否相等
    """
    if ignore_keys is None:
        ignore_keys = []
    
    keys1 = set(dict1.keys()) - set(ignore_keys)
    keys2 = set(dict2.keys()) - set(ignore_keys)
    
    if keys1 != keys2:
        return False
    
    for key in keys1:
        if dict1[key] != dict2[key]:
            return False
    
    return True


def mock_sleep(seconds: float = 0) -> None:
    """
    模拟sleep函数（不实际等待）
    
    Args:
        seconds: 睡眠秒数（被忽略）
    """
    pass


class MockLogger:
    """模拟日志记录器"""
    
    def __init__(self):
        self.logs = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': []
        }
    
    def debug(self, msg: str):
        self.logs['debug'].append(msg)
    
    def info(self, msg: str):
        self.logs['info'].append(msg)
    
    def warning(self, msg: str):
        self.logs['warning'].append(msg)
    
    def error(self, msg: str):
        self.logs['error'].append(msg)
    
    def critical(self, msg: str):
        self.logs['critical'].append(msg)
    
    def get_logs(self, level: str = None) -> List[str]:
        """获取日志记录"""
        if level:
            return self.logs.get(level, [])
        return [log for logs in self.logs.values() for log in logs]
    
    def clear(self):
        """清空日志"""
        for level in self.logs:
            self.logs[level] = []
