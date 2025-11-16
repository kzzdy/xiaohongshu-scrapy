"""小红书创作者中心API模块"""

from typing import Dict, Any, Optional, Tuple, List

from src.api.base import BaseAPIClient
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from xhs_utils.cookie_util import trans_cookies
from xhs_utils.xhs_creator_util import (
    get_common_headers,
    generate_xs,
    splice_str,
)


class XHSCreatorApi(BaseAPIClient):
    """小红书创作者中心API客户端

    提供小红书创作者中心的API接口，包括：
    - 获取已发布笔记信息
    - 笔记数据统计
    等功能。
    """

    def __init__(
        self,
        cookies_str: str,
        rate_limiter: RateLimiter,
        error_handler: ErrorHandler,
        timeout: int = 30,
        proxies: Optional[Dict[str, str]] = None,
    ):
        """初始化小红书创作者中心API客户端

        Args:
            cookies_str: Cookie字符串
            rate_limiter: 速率限制器实例
            error_handler: 错误处理器实例
            timeout: 请求超时时间（秒），默认30秒
            proxies: 代理配置
        """
        super().__init__(
            base_url="https://edith.xiaohongshu.com",
            rate_limiter=rate_limiter,
            error_handler=error_handler,
            timeout=timeout,
            proxies=proxies,
        )
        self.cookies_str = cookies_str
        self.cookies = trans_cookies(cookies_str)

    def _make_creator_request(
        self,
        method: str,
        api: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """内部请求方法，处理创作者中心特定的请求参数

        Args:
            method: HTTP方法
            api: API路径
            data: 请求体数据
            params: URL参数

        Returns:
            元组 (success, message, response_data)
        """
        try:
            # 获取a1参数
            a1 = self.cookies.get("a1", "")

            # 生成请求头
            headers = get_common_headers()

            # 构建完整URL
            if params:
                api = splice_str(api, params)

            # 生成xs和xt签名
            xs, xt, trans_data = generate_xs(a1, api, data if data else "")
            headers["x-s"] = xs
            headers["x-t"] = str(xt)

            # 发送请求
            kwargs = {
                "headers": headers,
                "cookies": self.cookies,
                "verify": False,  # 创作者API需要禁用SSL验证
            }

            if method.upper() == "GET":
                return self.get(api, **kwargs)
            elif method.upper() == "POST":
                if trans_data:
                    kwargs["data"] = trans_data
                return self.post(api, **kwargs)
            else:
                return False, f"不支持的HTTP方法: {method}", None

        except Exception as e:
            self.error_handler.log_error(f"创作者API请求失败: {api}", e)
            return False, str(e), None

    # ==================== 笔记管理相关API ====================

    def get_publish_note_info(
        self, page: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取已发布笔记信息

        Args:
            page: 页码，None表示获取第一页，-1表示没有更多数据

        Returns:
            元组 (success, message, data): 包含已发布笔记信息
            data中包含：
            - notes: 笔记列表
            - page: 下一页的页码（-1表示没有更多数据）
        """
        api = "/web_api/sns/v5/creator/note/user/posted"
        params = {"tab": "0"}

        if page is not None and page >= 0:
            params["page"] = str(page)

        return self._make_creator_request("GET", api, params=params)

    def get_all_publish_note_info(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取所有已发布笔记信息

        Returns:
            元组 (success, message, note_list): 包含所有已发布笔记列表
        """
        page = None
        note_list = []

        try:
            while True:
                success, msg, res_json = self.get_publish_note_info(page)

                if not success:
                    self.error_handler.log_error(f"获取发布笔记失败: {msg}")
                    return False, msg, note_list

                # 检查响应数据
                if not res_json or "data" not in res_json:
                    break

                # 获取笔记列表
                notes = res_json.get("data", {}).get("notes", [])
                note_list.extend(notes)

                # 获取下一页页码
                page = res_json.get("data", {}).get("page")

                # 如果page为-1，表示没有更多数据
                if page == -1:
                    break

        except Exception as e:
            self.error_handler.log_error("获取所有发布笔记失败", e)
            return False, str(e), note_list

        return True, "success", note_list

    def get_note_statistics(self, note_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取笔记数据统计

        Args:
            note_id: 笔记ID

        Returns:
            元组 (success, message, data): 包含笔记统计数据
            data中可能包含：
            - views: 浏览量
            - likes: 点赞数
            - collects: 收藏数
            - comments: 评论数
            - shares: 分享数
        """
        api = "/web_api/sns/v5/creator/note/statistics"
        params = {"note_id": note_id}

        return self._make_creator_request("GET", api, params=params)

    def get_note_detail(self, note_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取笔记详细信息（创作者视角）

        Args:
            note_id: 笔记ID

        Returns:
            元组 (success, message, data): 包含笔记详细信息
        """
        api = "/web_api/sns/v5/creator/note/detail"
        params = {"note_id": note_id}

        return self._make_creator_request("GET", api, params=params)

    # ==================== 数据分析相关API ====================

    def get_creator_overview(
        self, time_range: str = "7d"
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取创作者数据概览

        Args:
            time_range: 时间范围 (7d: 7天, 30d: 30天)

        Returns:
            元组 (success, message, data): 包含创作者数据概览
            data中可能包含：
            - total_views: 总浏览量
            - total_likes: 总点赞数
            - total_collects: 总收藏数
            - total_comments: 总评论数
            - new_fans: 新增粉丝数
        """
        api = "/web_api/sns/v5/creator/data/overview"
        params = {"time_range": time_range}

        return self._make_creator_request("GET", api, params=params)

    def get_fan_statistics(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取粉丝统计数据

        Returns:
            元组 (success, message, data): 包含粉丝统计数据
            data中可能包含：
            - total_fans: 总粉丝数
            - fan_growth: 粉丝增长趋势
            - fan_portrait: 粉丝画像
        """
        api = "/web_api/sns/v5/creator/data/fans"

        return self._make_creator_request("GET", api)

    # ==================== 内容管理相关API ====================

    def get_draft_list(self, page: int = 1) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取草稿列表

        Args:
            page: 页码

        Returns:
            元组 (success, message, data): 包含草稿列表
        """
        api = "/web_api/sns/v5/creator/note/draft/list"
        params = {"page": str(page)}

        return self._make_creator_request("GET", api, params=params)

    def get_all_draft_list(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取所有草稿

        Returns:
            元组 (success, message, draft_list): 包含所有草稿列表
        """
        page = 1
        draft_list = []

        try:
            while True:
                success, msg, res_json = self.get_draft_list(page)

                if not success:
                    self.error_handler.log_error(f"获取草稿列表失败: {msg}")
                    return False, msg, draft_list

                # 检查响应数据
                if not res_json or "data" not in res_json:
                    break

                # 获取草稿列表
                drafts = res_json.get("data", {}).get("drafts", [])
                if not drafts:
                    break

                draft_list.extend(drafts)
                page += 1

                # 检查是否还有更多数据
                has_more = res_json.get("data", {}).get("has_more", False)
                if not has_more:
                    break

        except Exception as e:
            self.error_handler.log_error("获取所有草稿失败", e)
            return False, str(e), draft_list

        return True, "success", draft_list

    def delete_note(self, note_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """删除笔记

        Args:
            note_id: 笔记ID

        Returns:
            元组 (success, message, data): 删除结果
        """
        api = "/web_api/sns/v5/creator/note/delete"
        data = {"note_id": note_id}

        return self._make_creator_request("POST", api, data=data)

    # ==================== 评论管理相关API ====================

    def get_note_comments(
        self, note_id: str, cursor: str = ""
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取笔记评论（创作者视角）

        Args:
            note_id: 笔记ID
            cursor: 游标

        Returns:
            元组 (success, message, data): 包含评论列表
        """
        api = "/web_api/sns/v5/creator/note/comment/list"
        params = {
            "note_id": note_id,
            "cursor": cursor,
        }

        return self._make_creator_request("GET", api, params=params)

    def reply_comment(
        self, note_id: str, comment_id: str, content: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """回复评论

        Args:
            note_id: 笔记ID
            comment_id: 评论ID
            content: 回复内容

        Returns:
            元组 (success, message, data): 回复结果
        """
        api = "/web_api/sns/v5/creator/note/comment/reply"
        data = {
            "note_id": note_id,
            "comment_id": comment_id,
            "content": content,
        }

        return self._make_creator_request("POST", api, data=data)

    def delete_comment(
        self, note_id: str, comment_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """删除评论

        Args:
            note_id: 笔记ID
            comment_id: 评论ID

        Returns:
            元组 (success, message, data): 删除结果
        """
        api = "/web_api/sns/v5/creator/note/comment/delete"
        data = {
            "note_id": note_id,
            "comment_id": comment_id,
        }

        return self._make_creator_request("POST", api, data=data)
