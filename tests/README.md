# 测试说明

本目录包含项目的所有测试代码，包括单元测试、集成测试和测试fixtures。

## 目录结构

```
tests/
├── unit/                      # 单元测试
│   └── __init__.py
├── integration/               # 集成测试
│   └── __init__.py
├── fixtures/                  # 测试数据和fixtures
│   ├── conftest.py           # Pytest fixtures定义
│   ├── helpers.py            # 测试辅助工具
│   ├── mock_responses.json   # 模拟API响应数据
│   ├── test_data.json        # 测试数据集
│   └── __init__.py
├── conftest.py               # 全局pytest配置
├── test_setup.py             # 测试环境验证
└── __init__.py
```

## 测试环境配置

测试环境已完成以下配置：

1. **测试框架**: pytest 8.3.5
2. **覆盖率工具**: pytest-cov 5.0.0
3. **Mock工具**: pytest-mock 3.14.1, responses 0.25.8
4. **异步测试**: pytest-asyncio 0.24.0
5. **测试fixtures**: 预定义的测试数据和对象
6. **测试标记**: unit, integration, slow, api

## 运行测试

### 基本命令

```bash
# 运行所有测试
python -m pytest

# 运行所有测试（详细输出）
python -m pytest -v

# 运行单元测试
python -m pytest tests/unit/

# 运行集成测试
python -m pytest tests/integration/

# 运行特定测试文件
python -m pytest tests/unit/test_config.py

# 运行特定测试函数
python -m pytest tests/unit/test_config.py::test_config_loading
```

### 覆盖率报告

```bash
# 生成HTML覆盖率报告
python -m pytest --cov=src --cov-report=html

# 生成终端覆盖率报告
python -m pytest --cov=src --cov-report=term-missing

# 生成XML覆盖率报告（用于CI/CD）
python -m pytest --cov=src --cov-report=xml
```

覆盖率报告将生成在以下位置：
- HTML报告: `htmlcov/index.html`
- XML报告: `coverage.xml`

### 使用标记运行测试

```bash
# 只运行单元测试
python -m pytest -m unit

# 只运行集成测试
python -m pytest -m integration

# 排除慢速测试
python -m pytest -m "not slow"

# 只运行API测试
python -m pytest -m api
```

### 其他有用选项

```bash
# 显示测试输出（print语句）
python -m pytest -s

# 在第一个失败时停止
python -m pytest -x

# 显示最慢的10个测试
python -m pytest --durations=10

# 并行运行测试（需要安装pytest-xdist）
python -m pytest -n auto

# 只运行上次失败的测试
python -m pytest --lf

# 详细的失败信息
python -m pytest -vv
```

## 编写测试

### 单元测试示例

```python
import pytest
from src.core.config import ConfigManager, SpiderConfig

@pytest.mark.unit
def test_config_loading(temp_env_file):
    """测试配置加载"""
    config_manager = ConfigManager(env_file=temp_env_file)
    config = config_manager.load_config()
    
    assert config is not None
    assert isinstance(config, SpiderConfig)
    assert config.cookies == "test_cookie_value"
    assert config.rate_limit == 3.0

@pytest.mark.unit
def test_config_validation(mock_config):
    """测试配置验证"""
    config_manager = ConfigManager()
    is_valid = config_manager.validate_config(mock_config)
    
    assert is_valid is True
```

### 使用Mock响应

```python
import responses
from src.api.xhs_pc import XHSPCApi
from tests.fixtures.helpers import load_mock_response

@pytest.mark.api
@responses.activate
def test_api_request(mock_rate_limiter, mock_error_handler):
    """测试API请求"""
    # 加载预定义的mock响应
    mock_data = load_mock_response('note_detail_success')
    
    # 设置mock响应
    responses.add(
        responses.POST,
        "https://edith.xiaohongshu.com/api/sns/web/v1/feed",
        json=mock_data,
        status=200
    )
    
    # 创建API客户端并测试
    api = XHSPCApi(
        rate_limiter=mock_rate_limiter,
        error_handler=mock_error_handler
    )
    success, msg, data = api.get_note_info("test_url", "test_cookies")
    
    assert success is True
    assert data is not None
```

### 使用Fixtures

```python
import pytest

@pytest.mark.unit
def test_with_fixtures(sample_note_data, temp_data_dir):
    """使用fixtures的测试"""
    from src.data.validator import DataValidator
    
    validator = DataValidator()
    validated_data = validator.validate_note(sample_note_data)
    
    assert validated_data is not None
    assert validated_data.note_id == sample_note_data["note_id"]
    assert validated_data.title == sample_note_data["title"]
```

### 测试异常处理

```python
import pytest
from src.core.config import ConfigManager, ConfigError

@pytest.mark.unit
def test_config_error(invalid_env_file):
    """测试配置错误处理"""
    config_manager = ConfigManager(env_file=invalid_env_file)
    
    with pytest.raises(ConfigError) as exc_info:
        config_manager.load_config()
    
    assert "Cookie" in str(exc_info.value)
```

### 参数化测试

```python
import pytest
from src.data.validator import DataValidator

@pytest.mark.unit
@pytest.mark.parametrize("filename,expected", [
    ("test.txt", "test.txt"),
    ("test/file.txt", "test_file.txt"),
    ("test:file.txt", "test_file.txt"),
    ("测试文件.txt", "测试文件.txt"),
])
def test_filename_validation(filename, expected):
    """测试文件名验证（参数化）"""
    validator = DataValidator()
    cleaned = validator.validate_filename(filename)
    assert cleaned == expected
```

### 使用Mock对象

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
def test_with_mock():
    """使用mock对象的测试"""
    from src.core.rate_limiter import RateLimiter
    
    # 创建mock对象
    mock_time = Mock()
    mock_time.return_value = 1000.0
    
    with patch('time.time', mock_time):
        limiter = RateLimiter(rate=3.0)
        limiter.acquire()
        
        # 验证mock被调用
        assert mock_time.called
```

### 集成测试示例

```python
import pytest
from tests.fixtures.helpers import create_test_file

@pytest.mark.integration
def test_full_workflow(temp_data_dir, sample_note_data):
    """测试完整工作流程"""
    from src.data.processor import DataProcessor
    from src.data.exporter import DataExporter
    
    # 处理数据
    processor = DataProcessor()
    processed_data = processor.handle_note_info(sample_note_data)
    
    # 导出数据
    exporter = DataExporter(output_dir=temp_data_dir)
    filepath = exporter.export([processed_data], "test_export.xlsx")
    
    # 验证结果
    assert Path(filepath).exists()
    assert Path(filepath).stat().st_size > 0
```

## 可用的Fixtures

测试环境提供了以下预定义的fixtures：

### 配置相关
- `temp_env_file`: 临时环境变量文件
- `invalid_env_file`: 无效的环境变量文件
- `mock_config`: 模拟配置对象

### 数据相关
- `sample_note_data`: 示例笔记数据
- `sample_video_note_data`: 示例视频笔记数据
- `sample_user_data`: 示例用户数据
- `invalid_note_data`: 无效的笔记数据
- `sample_notes_list`: 示例笔记列表
- `export_test_data`: 用于导出测试的数据

### API响应相关
- `mock_api_success_response`: 模拟成功的API响应
- `mock_api_error_response`: 模拟失败的API响应

### 文件系统相关
- `temp_data_dir`: 临时数据目录
- `temp_progress_file`: 临时进度文件
- `temp_log_dir`: 临时日志目录

### Mock对象相关
- `mock_rate_limiter`: 模拟速率限制器
- `mock_error_handler`: 模拟错误处理器
- `mock_logger`: 模拟日志记录器

### 辅助工具函数

从 `tests.fixtures.helpers` 导入：

```python
from tests.fixtures.helpers import (
    load_mock_response,      # 加载模拟API响应
    load_test_data,          # 加载测试数据
    create_mock_response,    # 创建模拟HTTP响应
    assert_file_exists,      # 断言文件存在
    create_test_file,        # 创建测试文件
    MockLogger              # 模拟日志记录器类
)
```

## 测试标记

使用pytest标记来分类测试：

```python
import pytest

@pytest.mark.unit
def test_something():
    """单元测试"""
    pass

@pytest.mark.integration
def test_integration():
    """集成测试"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """慢速测试"""
    pass

@pytest.mark.api
def test_api_call():
    """API测试"""
    pass
```

运行特定标记的测试：
```bash
python -m pytest -m unit
python -m pytest -m "not slow"
python -m pytest -m "unit and not slow"
```


## 测试最佳实践

### 1. 测试命名

- 测试文件: `test_*.py` 或 `*_test.py`
- 测试类: `Test*`
- 测试函数: `test_*`
- 使用描述性名称，清楚表达测试目的

```python
# 好的命名
def test_rate_limiter_blocks_when_limit_exceeded():
    pass

# 不好的命名
def test_limiter():
    pass
```

### 2. 测试结构

使用 AAA (Arrange-Act-Assert) 模式：

```python
def test_example():
    # Arrange - 准备测试数据和环境
    config = SpiderConfig(cookies="test")
    
    # Act - 执行被测试的操作
    result = config.validate()
    
    # Assert - 验证结果
    assert result is True
```

### 3. 测试隔离

- 每个测试应该独立运行
- 不依赖其他测试的执行顺序
- 使用fixtures提供测试数据
- 测试后清理资源

```python
@pytest.fixture
def temp_file(tmp_path):
    """创建临时文件，测试后自动清理"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    yield str(file_path)
    # 清理会自动进行（tmp_path是pytest内置fixture）
```

### 4. 测试覆盖率

- 目标覆盖率: 70%以上
- 重点测试核心业务逻辑
- 不要为了覆盖率而写无意义的测试
- 关注边界条件和异常情况

### 5. Mock使用原则

- 只mock外部依赖（API、数据库、文件系统）
- 不要mock被测试的代码
- 使用真实数据结构，避免过度简化
- 验证mock的调用次数和参数

### 6. 测试文档

- 每个测试函数添加docstring
- 说明测试目的和预期结果
- 复杂测试添加注释

```python
def test_rate_limiter_with_concurrent_requests():
    """
    测试速率限制器在并发请求下的行为
    
    验证点：
    1. 并发请求不会超过速率限制
    2. 所有请求最终都能完成
    3. 限流统计正确
    """
    pass
```

## 持续集成

### GitHub Actions配置示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          python -m pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 故障排查

### 常见问题

1. **导入错误**
   ```bash
   # 确保项目根目录在Python路径中
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Fixture未找到**
   - 检查 `conftest.py` 是否正确配置
   - 确认fixture定义在正确的位置

3. **Mock不生效**
   - 检查mock的路径是否正确
   - 确认使用了正确的装饰器顺序

4. **覆盖率不准确**
   - 清除缓存: `python -m pytest --cache-clear`
   - 删除 `.coverage` 文件重新运行

## 参考资源

- [Pytest官方文档](https://docs.pytest.org/)
- [Pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [Responses库文档](https://github.com/getsentry/responses)
- [Python测试最佳实践](https://docs.python-guide.org/writing/tests/)
