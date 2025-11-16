# API层文档

## 概述

API层提供了与小红书平台交互的统一接口，包括PC端API和创作者中心API。所有API客户端都继承自`BaseAPIClient`，集成了速率限制、错误处理和会话管理功能。

## 架构

```
src/api/
├── __init__.py          # 模块导出
├── base.py              # 基础API客户端
├── xhs_pc.py            # 小红书PC端API
└── xhs_creator.py       # 创作者中心API
```

## 核心组件

### 1. BaseAPIClient

基础API客户端，提供统一的HTTP请求接口。

**特性：**
- 自动速率限制
- 统一错误处理
- 会话管理和连接复用
- 自动重试机制
- 支持上下文管理器

**使用示例：**

```python
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from src.api.base import BaseAPIClient

# 初始化依赖
rate_limiter = RateLimiter(rate=3.0)
error_handler = ErrorHandler()

# 创建客户端
with BaseAPIClient(
    base_url="https://api.example.com",
    rate_limiter=rate_limiter,
    error_handler=error_handler,
    timeout=30,
) as client:
    success, msg, data = client.get("/endpoint")
    if success:
        print(data)
```

### 2. XHSPCApi

小红书PC端API客户端，提供完整的PC端功能。

**主要功能：**

#### 用户相关
- `get_user_info(user_id)` - 获取用户信息
- `get_user_all_notes(user_url)` - 获取用户所有笔记
- `get_user_all_like_note_info(user_url)` - 获取用户喜欢的笔记
- `get_user_all_collect_note_info(user_url)` - 获取用户收藏的笔记

#### 笔记相关
- `get_note_info(url)` - 获取笔记详细信息
- `get_note_all_comment(url)` - 获取笔记所有评论

#### 搜索相关
- `search_note(query, page, ...)` - 搜索笔记
- `search_some_note(query, require_num, ...)` - 搜索指定数量的笔记
- `search_user(query, page)` - 搜索用户
- `search_some_user(query, require_num)` - 搜索指定数量的用户

#### 主页相关
- `get_homefeed_all_channel()` - 获取所有频道
- `get_homefeed_recommend(category, ...)` - 获取推荐笔记
- `get_homefeed_recommend_by_num(category, require_num)` - 获取指定数量的推荐笔记

#### 消息通知
- `get_unread_message()` - 获取未读消息
- `get_all_mentions()` - 获取所有@提醒
- `get_all_likes_and_collects()` - 获取所有赞和收藏
- `get_all_new_connections()` - 获取所有新增关注

**使用示例：**

```python
from src.core.config import ConfigManager
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from src.api.xhs_pc import XHSPCApi

# 加载配置
config_manager = ConfigManager()
config = config_manager.load_config()

# 初始化依赖
rate_limiter = RateLimiter(rate=config.rate_limit)
error_handler = ErrorHandler(log_level=config.log_level)

# 创建API客户端
api = XHSPCApi(
    cookies_str=config.cookies,
    rate_limiter=rate_limiter,
    error_handler=error_handler,
    timeout=config.timeout,
    proxies=config.proxy,
)

# 获取笔记信息
note_url = "https://www.xiaohongshu.com/explore/..."
success, msg, data = api.get_note_info(note_url)
if success:
    print(f"笔记标题: {data['data']['items'][0]['note_card']['title']}")

# 搜索笔记
success, msg, notes = api.search_some_note("美食", require_num=10)
if success:
    print(f"找到 {len(notes)} 条笔记")

# 获取用户所有笔记
user_url = "https://www.xiaohongshu.com/user/profile/..."
success, msg, notes = api.get_user_all_notes(user_url)
if success:
    print(f"用户共有 {len(notes)} 条笔记")
```

### 3. XHSCreatorApi

小红书创作者中心API客户端，提供创作者专属功能。

**主要功能：**

#### 笔记管理
- `get_publish_note_info(page)` - 获取已发布笔记
- `get_all_publish_note_info()` - 获取所有已发布笔记
- `get_note_statistics(note_id)` - 获取笔记统计数据
- `get_note_detail(note_id)` - 获取笔记详细信息
- `delete_note(note_id)` - 删除笔记

#### 数据分析
- `get_creator_overview(time_range)` - 获取创作者数据概览
- `get_fan_statistics()` - 获取粉丝统计数据

#### 内容管理
- `get_draft_list(page)` - 获取草稿列表
- `get_all_draft_list()` - 获取所有草稿

#### 评论管理
- `get_note_comments(note_id, cursor)` - 获取笔记评论
- `reply_comment(note_id, comment_id, content)` - 回复评论
- `delete_comment(note_id, comment_id)` - 删除评论

**使用示例：**

```python
from src.core.config import ConfigManager
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from src.api.xhs_creator import XHSCreatorApi

# 加载配置
config_manager = ConfigManager()
config = config_manager.load_config()

# 初始化依赖
rate_limiter = RateLimiter(rate=config.rate_limit)
error_handler = ErrorHandler(log_level=config.log_level)

# 创建API客户端
api = XHSCreatorApi(
    cookies_str=config.cookies,
    rate_limiter=rate_limiter,
    error_handler=error_handler,
    timeout=config.timeout,
    proxies=config.proxy,
)

# 获取所有已发布笔记
success, msg, notes = api.get_all_publish_note_info()
if success:
    print(f"共有 {len(notes)} 条已发布笔记")
    for note in notes:
        print(f"- {note['title']}")

# 获取创作者数据概览
success, msg, data = api.get_creator_overview(time_range="7d")
if success:
    overview = data['data']
    print(f"7天数据概览:")
    print(f"- 总浏览量: {overview.get('total_views', 0)}")
    print(f"- 总点赞数: {overview.get('total_likes', 0)}")
    print(f"- 新增粉丝: {overview.get('new_fans', 0)}")
```

## 返回值格式

所有API方法都返回统一的元组格式：

```python
(success: bool, message: str, data: Optional[Dict[str, Any]])
```

- `success`: 请求是否成功
- `message`: 成功或错误消息
- `data`: 响应数据（JSON格式），失败时为None

对于批量获取方法（如`get_all_*`），返回格式为：

```python
(success: bool, message: str, items: List[Dict[str, Any]])
```

## 错误处理

API层集成了统一的错误处理机制：

1. **网络错误**：自动重试（最多3次）
2. **速率限制**：自动等待
3. **业务错误**：记录日志并返回错误信息
4. **致命错误**：记录详细日志

所有错误都会被记录到日志文件中：
- `logs/spider_YYYY-MM-DD.log` - 所有日志
- `logs/error_YYYY-MM-DD.log` - 仅错误日志

## 速率限制

API层自动应用速率限制，默认为3请求/秒。可以通过配置文件调整：

```env
RATE_LIMIT=3.0
```

速率限制器使用令牌桶算法，确保请求平滑分布，避免突发流量。

## 会话管理

API层使用`requests.Session`进行连接复用，提高性能：

- 连接池大小：10
- 最大连接数：20
- 自动重试：3次
- 重试间隔：1s, 2s, 4s（指数退避）

## 代理支持

所有API客户端都支持代理配置：

```python
proxies = {
    "http": "http://proxy.example.com:8080",
    "https": "https://proxy.example.com:8080",
}

api = XHSPCApi(
    cookies_str=cookies,
    rate_limiter=rate_limiter,
    error_handler=error_handler,
    proxies=proxies,
)
```

或通过环境变量配置：

```env
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=https://proxy.example.com:8080
```

## 最佳实践

1. **使用上下文管理器**：确保会话正确关闭
   ```python
   with XHSPCApi(...) as api:
       success, msg, data = api.get_note_info(url)
   ```

2. **检查返回值**：始终检查`success`标志
   ```python
   success, msg, data = api.get_note_info(url)
   if not success:
       print(f"请求失败: {msg}")
       return
   ```

3. **使用批量方法**：对于需要获取所有数据的场景，使用`get_all_*`方法
   ```python
   # 推荐
   success, msg, notes = api.get_all_publish_note_info()
   
   # 不推荐
   page = None
   notes = []
   while True:
       success, msg, data = api.get_publish_note_info(page)
       # ...
   ```

4. **合理设置速率限制**：根据实际需求调整速率
   ```python
   # 开发测试：较低速率
   rate_limiter = RateLimiter(rate=1.0)
   
   # 生产环境：正常速率
   rate_limiter = RateLimiter(rate=3.0)
   ```

5. **处理异常**：使用try-except捕获异常
   ```python
   try:
       success, msg, data = api.get_note_info(url)
       if success:
           # 处理数据
           pass
   except Exception as e:
       error_handler.log_error("获取笔记失败", e)
   ```

## 测试

运行验证脚本测试API层：

```bash
python verify_api_layer.py
```

## 迁移指南

从旧API迁移到新API：

### 旧代码
```python
from apis.xhs_pc_apis import XHS_Apis

api = XHS_Apis()
success, msg, data = api.get_note_info(url, cookies_str, proxies)
```

### 新代码
```python
from src.api.xhs_pc import XHSPCApi
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler

rate_limiter = RateLimiter(rate=3.0)
error_handler = ErrorHandler()

api = XHSPCApi(
    cookies_str=cookies_str,
    rate_limiter=rate_limiter,
    error_handler=error_handler,
    proxies=proxies,
)

success, msg, data = api.get_note_info(url)
```

主要变化：
1. 导入路径变更
2. 需要传入`rate_limiter`和`error_handler`
3. `cookies_str`和`proxies`在初始化时传入
4. 方法调用时不再需要传入`cookies_str`和`proxies`

## 注意事项

1. **Cookie有效性**：确保Cookie有效且未过期
2. **请求频率**：遵守平台规则，避免过快请求
3. **错误处理**：妥善处理各种错误情况
4. **日志监控**：定期检查日志文件
5. **代理使用**：如需使用代理，确保代理稳定可用
