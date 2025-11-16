# 测试快速入门指南

## 5分钟快速开始

### 1. 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

### 2. 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行并查看覆盖率
python -m pytest --cov=src --cov-report=html
```

### 3. 查看覆盖率报告

在浏览器中打开 `htmlcov/index.html`

## 编写第一个测试

### 步骤1: 创建测试文件

在 `tests/unit/` 目录下创建 `test_my_module.py`

### 步骤2: 编写测试

```python
import pytest

@pytest.mark.unit
def test_my_function():
    """测试我的函数"""
    # Arrange - 准备
    input_data = "test"
    
    # Act - 执行
    result = my_function(input_data)
    
    # Assert - 验证
    assert result == "expected_output"
```

### 步骤3: 运行测试

```bash
python -m pytest tests/unit/test_my_module.py -v
```

## 使用Fixtures

### 使用预定义的fixtures

```python
def test_with_sample_data(sample_note_data):
    """使用示例数据的测试"""
    assert sample_note_data["note_id"] is not None
```

### 创建自定义fixture

```python
@pytest.fixture
def my_custom_fixture():
    """自定义fixture"""
    data = {"key": "value"}
    return data

def test_with_custom_fixture(my_custom_fixture):
    """使用自定义fixture"""
    assert my_custom_fixture["key"] == "value"
```

## Mock API调用

```python
import responses
from tests.fixtures.helpers import load_mock_response

@responses.activate
def test_api_call():
    """测试API调用"""
    # 加载预定义的mock响应
    mock_data = load_mock_response('note_detail_success')
    
    # 设置mock
    responses.add(
        responses.POST,
        "https://api.example.com/endpoint",
        json=mock_data,
        status=200
    )
    
    # 执行测试
    result = call_api()
    assert result is not None
```

## 常用命令速查

```bash
# 运行所有测试
python -m pytest

# 运行单元测试
python -m pytest tests/unit/ -m unit

# 运行特定文件
python -m pytest tests/unit/test_config.py

# 运行特定测试
python -m pytest tests/unit/test_config.py::test_config_loading

# 显示详细输出
python -m pytest -v

# 显示print输出
python -m pytest -s

# 第一个失败时停止
python -m pytest -x

# 生成覆盖率报告
python -m pytest --cov=src --cov-report=html

# 只运行上次失败的测试
python -m pytest --lf

# 显示最慢的测试
python -m pytest --durations=10
```

## 可用的测试标记

```bash
# 单元测试
python -m pytest -m unit

# 集成测试
python -m pytest -m integration

# 排除慢速测试
python -m pytest -m "not slow"

# API测试
python -m pytest -m api
```

## 可用的Fixtures速查

### 配置相关
- `temp_env_file` - 临时环境变量文件
- `mock_config` - 模拟配置对象

### 数据相关
- `sample_note_data` - 示例笔记数据
- `sample_video_note_data` - 示例视频数据
- `sample_user_data` - 示例用户数据
- `export_test_data` - 导出测试数据

### 文件系统
- `temp_data_dir` - 临时数据目录
- `temp_log_dir` - 临时日志目录
- `temp_progress_file` - 临时进度文件

### Mock对象
- `mock_rate_limiter` - 模拟速率限制器
- `mock_error_handler` - 模拟错误处理器
- `mock_logger` - 模拟日志记录器

## 辅助工具函数

```python
from tests.fixtures.helpers import (
    load_mock_response,      # 加载mock响应
    load_test_data,          # 加载测试数据
    create_mock_response,    # 创建mock响应
    assert_file_exists,      # 断言文件存在
    create_test_file,        # 创建测试文件
    MockLogger              # Mock日志记录器
)
```

## 测试模板

### 单元测试模板

```python
import pytest

@pytest.mark.unit
def test_function_name():
    """测试描述"""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

### 集成测试模板

```python
import pytest

@pytest.mark.integration
def test_integration_scenario(temp_data_dir):
    """集成测试描述"""
    # Setup
    component_a = ComponentA()
    component_b = ComponentB()
    
    # Execute
    result = component_a.process(component_b.get_data())
    
    # Verify
    assert result is not None
    assert result.status == "success"
```

### API测试模板

```python
import pytest
import responses
from tests.fixtures.helpers import load_mock_response

@pytest.mark.api
@responses.activate
def test_api_endpoint():
    """API测试描述"""
    # Setup mock
    mock_data = load_mock_response('api_success_response')
    responses.add(
        responses.POST,
        "https://api.example.com/endpoint",
        json=mock_data,
        status=200
    )
    
    # Execute
    result = api_client.call_endpoint()
    
    # Verify
    assert result.success is True
```

## 下一步

- 阅读完整文档: [tests/README.md](README.md)
- 查看测试示例: [tests/test_setup.py](test_setup.py)
- 了解fixtures: [tests/fixtures/conftest.py](fixtures/conftest.py)
