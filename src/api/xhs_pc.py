"""小红书PC端API模块"""

from typing import Dict, Any, Optional, Tuple, List
import json
import urllib.parse

from src.api.base import BaseAPIClient
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from xhs_utils.xhs_util import (
    splice_str,
    generate_request_params,
    generate_x_b3_traceid,
)


class XHSPCApi(BaseAPIClient):
    """小红书PC端API客户端

    提供小红书PC端的所有API接口，包括：
    - 用户信息查询
    - 笔记信息查询
    - 搜索功能
    - 评论获取
    - 消息通知
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
        """初始化小红书PC端API客户端

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

    def _make_request(
        self,
        method: str,
        api: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """内部请求方法，处理小红书特定的请求参数

        Args:
            method: HTTP方法
            api: API路径
            data: 请求体数据
            params: URL参数

        Returns:
            元组 (success, message, response_data)
        """
        try:
            # 生成请求参数
            headers, cookies, trans_data = generate_request_params(
                self.cookies_str, api, data if data else ""
            )

            # 构建完整URL
            if params:
                api = splice_str(api, params)

            # 发送请求
            kwargs = {
                "headers": headers,
                "cookies": cookies,
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
            self.error_handler.log_error(f"请求失败: {api}", e)
            return False, str(e), None

    # ==================== 主页相关API ====================

    def get_homefeed_all_channel(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取主页的所有频道

        Returns:
            元组 (success, message, data): 包含所有频道信息
        """
        api = "/api/sns/web/v1/homefeed/category"
        return self._make_request("GET", api)

    def get_homefeed_recommend(
        self,
        category: str,
        cursor_score: str,
        refresh_type: int,
        note_index: int,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取主页推荐的笔记

        Args:
            category: 频道类别
            cursor_score: 游标分数
            refresh_type: 刷新类型
            note_index: 笔记索引

        Returns:
            元组 (success, message, data): 包含推荐笔记列表
        """
        api = "/api/sns/web/v1/homefeed"
        data = {
            "cursor_score": cursor_score,
            "num": 20,
            "refresh_type": refresh_type,
            "note_index": note_index,
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
            "category": category,
            "search_key": "",
            "need_num": 10,
            "image_formats": ["jpg", "webp", "avif"],
            "need_filter_image": False,
        }
        return self._make_request("POST", api, data=data)

    def get_homefeed_recommend_by_num(
        self,
        category: str,
        require_num: int,
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """根据数量获取主页推荐的笔记

        Args:
            category: 频道类别
            require_num: 需要获取的笔记数量

        Returns:
            元组 (success, message, note_list): 包含指定数量的笔记列表
        """
        cursor_score, refresh_type, note_index = "", 1, 0
        note_list = []

        try:
            while True:
                success, msg, res_json = self.get_homefeed_recommend(
                    category, cursor_score, refresh_type, note_index
                )
                if not success:
                    raise Exception(msg)

                if "items" not in res_json.get("data", {}):
                    break

                notes = res_json["data"]["items"]
                note_list.extend(notes)
                cursor_score = res_json["data"]["cursor_score"]
                refresh_type = 3
                note_index += 20

                if len(note_list) >= require_num:
                    break

        except Exception as e:
            return False, str(e), note_list

        if len(note_list) > require_num:
            note_list = note_list[:require_num]

        return True, "success", note_list

    # ==================== 用户相关API ====================

    def get_user_info(self, user_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            元组 (success, message, data): 包含用户信息
        """
        api = "/api/sns/web/v1/user/otherinfo"
        params = {"target_user_id": user_id}
        return self._make_request("GET", api, params=params)

    def get_user_self_info(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取当前用户自己的信息（方式1）

        Returns:
            元组 (success, message, data): 包含用户信息
        """
        api = "/api/sns/web/v1/user/selfinfo"
        return self._make_request("GET", api)

    def get_user_self_info2(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取当前用户自己的信息（方式2）

        Returns:
            元组 (success, message, data): 包含用户信息
        """
        api = "/api/sns/web/v2/user/me"
        return self._make_request("GET", api)

    def get_user_note_info(
        self,
        user_id: str,
        cursor: str,
        xsec_token: str = "",
        xsec_source: str = "",
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取用户指定位置的笔记

        Args:
            user_id: 用户ID
            cursor: 游标
            xsec_token: 安全令牌
            xsec_source: 安全来源

        Returns:
            元组 (success, message, data): 包含笔记列表
        """
        api = "/api/sns/web/v1/user_posted"
        params = {
            "num": "30",
            "cursor": cursor,
            "user_id": user_id,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
            "xsec_source": xsec_source,
        }
        return self._make_request("GET", api, params=params)

    def get_user_all_notes(self, user_url: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取用户所有笔记

        Args:
            user_url: 用户主页URL

        Returns:
            元组 (success, message, note_list): 包含所有笔记列表
        """
        cursor = ""
        note_list = []

        try:
            # 解析URL获取用户ID和参数
            url_parse = urllib.parse.urlparse(user_url)
            user_id = url_parse.path.split("/")[-1]
            kvs = url_parse.query.split("&") if url_parse.query else []
            kv_dict = {kv.split("=")[0]: kv.split("=")[1] for kv in kvs if "=" in kv}
            xsec_token = kv_dict.get("xsec_token", "")
            xsec_source = kv_dict.get("xsec_source", "pc_search")

            while True:
                success, msg, res_json = self.get_user_note_info(
                    user_id, cursor, xsec_token, xsec_source
                )
                if not success:
                    raise Exception(msg)

                notes = res_json.get("data", {}).get("notes", [])
                if "cursor" in res_json.get("data", {}):
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break

                note_list.extend(notes)

                if len(notes) == 0 or not res_json.get("data", {}).get("has_more", False):
                    break

        except Exception as e:
            return False, str(e), note_list

        return True, "success", note_list

    def get_user_like_note_info(
        self,
        user_id: str,
        cursor: str,
        xsec_token: str = "",
        xsec_source: str = "",
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取用户指定位置喜欢的笔记

        Args:
            user_id: 用户ID
            cursor: 游标
            xsec_token: 安全令牌
            xsec_source: 安全来源

        Returns:
            元组 (success, message, data): 包含喜欢的笔记列表
        """
        api = "/api/sns/web/v1/note/like/page"
        params = {
            "num": "30",
            "cursor": cursor,
            "user_id": user_id,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
            "xsec_source": xsec_source,
        }
        return self._make_request("GET", api, params=params)

    def get_user_all_like_note_info(self, user_url: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取用户所有喜欢的笔记

        Args:
            user_url: 用户主页URL

        Returns:
            元组 (success, message, note_list): 包含所有喜欢的笔记列表
        """
        cursor = ""
        note_list = []

        try:
            url_parse = urllib.parse.urlparse(user_url)
            user_id = url_parse.path.split("/")[-1]
            kvs = url_parse.query.split("&") if url_parse.query else []
            kv_dict = {kv.split("=")[0]: kv.split("=")[1] for kv in kvs if "=" in kv}
            xsec_token = kv_dict.get("xsec_token", "")
            xsec_source = kv_dict.get("xsec_source", "pc_user")

            while True:
                success, msg, res_json = self.get_user_like_note_info(
                    user_id, cursor, xsec_token, xsec_source
                )
                if not success:
                    raise Exception(msg)

                notes = res_json.get("data", {}).get("notes", [])
                if "cursor" in res_json.get("data", {}):
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break

                note_list.extend(notes)

                if len(notes) == 0 or not res_json.get("data", {}).get("has_more", False):
                    break

        except Exception as e:
            return False, str(e), note_list

        return True, "success", note_list

    def get_user_collect_note_info(
        self,
        user_id: str,
        cursor: str,
        xsec_token: str = "",
        xsec_source: str = "",
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取用户指定位置收藏的笔记

        Args:
            user_id: 用户ID
            cursor: 游标
            xsec_token: 安全令牌
            xsec_source: 安全来源

        Returns:
            元组 (success, message, data): 包含收藏的笔记列表
        """
        api = "/api/sns/web/v2/note/collect/page"
        params = {
            "num": "30",
            "cursor": cursor,
            "user_id": user_id,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
            "xsec_source": xsec_source,
        }
        return self._make_request("GET", api, params=params)

    def get_user_all_collect_note_info(
        self, user_url: str
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取用户所有收藏的笔记

        Args:
            user_url: 用户主页URL

        Returns:
            元组 (success, message, note_list): 包含所有收藏的笔记列表
        """
        cursor = ""
        note_list = []

        try:
            url_parse = urllib.parse.urlparse(user_url)
            user_id = url_parse.path.split("/")[-1]
            kvs = url_parse.query.split("&") if url_parse.query else []
            kv_dict = {kv.split("=")[0]: kv.split("=")[1] for kv in kvs if "=" in kv}
            xsec_token = kv_dict.get("xsec_token", "")
            xsec_source = kv_dict.get("xsec_source", "pc_search")

            while True:
                success, msg, res_json = self.get_user_collect_note_info(
                    user_id, cursor, xsec_token, xsec_source
                )
                if not success:
                    raise Exception(msg)

                notes = res_json.get("data", {}).get("notes", [])
                if "cursor" in res_json.get("data", {}):
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break

                note_list.extend(notes)

                if len(notes) == 0 or not res_json.get("data", {}).get("has_more", False):
                    break

        except Exception as e:
            return False, str(e), note_list

        return True, "success", note_list

    # ==================== 笔记相关API ====================

    def get_note_info(self, url: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取笔记详细信息

        Args:
            url: 笔记URL

        Returns:
            元组 (success, message, data): 包含笔记详细信息
        """
        try:
            url_parse = urllib.parse.urlparse(url)
            note_id = url_parse.path.split("/")[-1]
            kvs = url_parse.query.split("&") if url_parse.query else []
            kv_dict = {kv.split("=")[0]: kv.split("=")[1] for kv in kvs if "=" in kv}

            api = "/api/sns/web/v1/feed"
            data = {
                "source_note_id": note_id,
                "image_formats": ["jpg", "webp", "avif"],
                "extra": {"need_body_topic": "1"},
                "xsec_source": kv_dict.get("xsec_source", "pc_search"),
                "xsec_token": kv_dict.get("xsec_token", ""),
            }

            return self._make_request("POST", api, data=data)

        except Exception as e:
            self.error_handler.log_error(f"解析笔记URL失败: {url}", e)
            return False, str(e), None

    # ==================== 搜索相关API ====================

    def get_search_keyword(self, word: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取搜索关键词推荐

        Args:
            word: 搜索关键词

        Returns:
            元组 (success, message, data): 包含关键词推荐
        """
        api = "/api/sns/web/v1/search/recommend"
        params = {"keyword": urllib.parse.quote(word)}
        return self._make_request("GET", api, params=params)

    def search_note(
        self,
        query: str,
        page: int = 1,
        sort_type_choice: int = 0,
        note_type: int = 0,
        note_time: int = 0,
        note_range: int = 0,
        pos_distance: int = 0,
        geo: str = "",
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """搜索笔记

        Args:
            query: 搜索关键词
            page: 页数
            sort_type_choice: 排序方式 (0:综合, 1:最新, 2:最多点赞, 3:最多评论, 4:最多收藏)
            note_type: 笔记类型 (0:不限, 1:视频笔记, 2:普通笔记)
            note_time: 笔记时间 (0:不限, 1:一天内, 2:一周内, 3:半年内)
            note_range: 笔记范围 (0:不限, 1:已看过, 2:未看过, 3:已关注)
            pos_distance: 位置距离 (0:不限, 1:同城, 2:附近)
            geo: 地理位置信息（JSON字符串）

        Returns:
            元组 (success, message, data): 包含搜索结果
        """
        # 排序方式映射
        sort_type_map = {
            0: "general",
            1: "time_descending",
            2: "popularity_descending",
            3: "comment_descending",
            4: "collect_descending",
        }
        sort_type = sort_type_map.get(sort_type_choice, "general")

        # 笔记类型映射
        note_type_map = {0: "不限", 1: "视频笔记", 2: "普通笔记"}
        filter_note_type = note_type_map.get(note_type, "不限")

        # 笔记时间映射
        note_time_map = {0: "不限", 1: "一天内", 2: "一周内", 3: "半年内"}
        filter_note_time = note_time_map.get(note_time, "不限")

        # 笔记范围映射
        note_range_map = {0: "不限", 1: "已看过", 2: "未看过", 3: "已关注"}
        filter_note_range = note_range_map.get(note_range, "不限")

        # 位置距离映射
        pos_distance_map = {0: "不限", 1: "同城", 2: "附近"}
        filter_pos_distance = pos_distance_map.get(pos_distance, "不限")

        # 处理地理位置
        if geo:
            geo = json.dumps(geo, separators=(",", ":"))

        api = "/api/sns/web/v1/search/notes"
        data = {
            "keyword": query,
            "page": page,
            "page_size": 20,
            "search_id": generate_x_b3_traceid(21),
            "sort": "general",
            "note_type": 0,
            "ext_flags": [],
            "filters": [
                {"tags": [sort_type], "type": "sort_type"},
                {"tags": [filter_note_type], "type": "filter_note_type"},
                {"tags": [filter_note_time], "type": "filter_note_time"},
                {"tags": [filter_note_range], "type": "filter_note_range"},
                {"tags": [filter_pos_distance], "type": "filter_pos_distance"},
            ],
            "geo": geo,
            "image_formats": ["jpg", "webp", "avif"],
        }

        return self._make_request("POST", api, data=data)

    def search_some_note(
        self,
        query: str,
        require_num: int,
        sort_type_choice: int = 0,
        note_type: int = 0,
        note_time: int = 0,
        note_range: int = 0,
        pos_distance: int = 0,
        geo: str = "",
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """搜索指定数量的笔记

        Args:
            query: 搜索关键词
            require_num: 需要的笔记数量
            sort_type_choice: 排序方式
            note_type: 笔记类型
            note_time: 笔记时间
            note_range: 笔记范围
            pos_distance: 位置距离
            geo: 地理位置信息

        Returns:
            元组 (success, message, note_list): 包含指定数量的笔记列表
        """
        page = 1
        note_list = []

        try:
            while True:
                success, msg, res_json = self.search_note(
                    query,
                    page,
                    sort_type_choice,
                    note_type,
                    note_time,
                    note_range,
                    pos_distance,
                    geo,
                )
                if not success:
                    raise Exception(msg)

                if "items" not in res_json.get("data", {}):
                    break

                notes = res_json["data"]["items"]
                note_list.extend(notes)
                page += 1

                if len(note_list) >= require_num or not res_json.get("data", {}).get(
                    "has_more", False
                ):
                    break

        except Exception as e:
            return False, str(e), note_list

        if len(note_list) > require_num:
            note_list = note_list[:require_num]

        return True, "success", note_list

    def search_user(self, query: str, page: int = 1) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """搜索用户

        Args:
            query: 搜索关键词
            page: 页数

        Returns:
            元组 (success, message, data): 包含用户搜索结果
        """
        api = "/api/sns/web/v1/search/usersearch"
        data = {
            "search_user_request": {
                "keyword": query,
                "search_id": "2dn9they1jbjxwawlo4xd",
                "page": page,
                "page_size": 15,
                "biz_type": "web_search_user",
                "request_id": "22471139-1723999898524",
            }
        }
        return self._make_request("POST", api, data=data)

    def search_some_user(
        self, query: str, require_num: int
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """搜索指定数量的用户

        Args:
            query: 搜索关键词
            require_num: 需要的用户数量

        Returns:
            元组 (success, message, user_list): 包含指定数量的用户列表
        """
        page = 1
        user_list = []

        try:
            while True:
                success, msg, res_json = self.search_user(query, page)
                if not success:
                    raise Exception(msg)

                if "users" not in res_json.get("data", {}):
                    break

                users = res_json["data"]["users"]
                user_list.extend(users)
                page += 1

                if len(user_list) >= require_num or not res_json.get("data", {}).get(
                    "has_more", False
                ):
                    break

        except Exception as e:
            return False, str(e), user_list

        if len(user_list) > require_num:
            user_list = user_list[:require_num]

        return True, "success", user_list

    # ==================== 评论相关API ====================

    def get_note_out_comment(
        self, note_id: str, cursor: str, xsec_token: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取笔记的一级评论

        Args:
            note_id: 笔记ID
            cursor: 游标
            xsec_token: 安全令牌

        Returns:
            元组 (success, message, data): 包含一级评论列表
        """
        api = "/api/sns/web/v2/comment/page"
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
        }
        return self._make_request("GET", api, params=params)

    def get_note_all_out_comment(
        self, note_id: str, xsec_token: str
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取笔记的所有一级评论

        Args:
            note_id: 笔记ID
            xsec_token: 安全令牌

        Returns:
            元组 (success, message, comment_list): 包含所有一级评论
        """
        cursor = ""
        comment_list = []

        try:
            while True:
                success, msg, res_json = self.get_note_out_comment(note_id, cursor, xsec_token)
                if not success:
                    raise Exception(msg)

                comments = res_json.get("data", {}).get("comments", [])
                if "cursor" in res_json.get("data", {}):
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break

                comment_list.extend(comments)

                if len(comments) == 0 or not res_json.get("data", {}).get("has_more", False):
                    break

        except Exception as e:
            return False, str(e), comment_list

        return True, "success", comment_list

    def get_note_inner_comment(
        self, comment: Dict[str, Any], cursor: str, xsec_token: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取笔记的二级评论

        Args:
            comment: 一级评论对象
            cursor: 游标
            xsec_token: 安全令牌

        Returns:
            元组 (success, message, data): 包含二级评论列表
        """
        api = "/api/sns/web/v2/comment/sub/page"
        params = {
            "note_id": comment["note_id"],
            "root_comment_id": comment["id"],
            "num": "10",
            "cursor": cursor,
            "image_formats": "jpg,webp,avif",
            "top_comment_id": "",
            "xsec_token": xsec_token,
        }
        return self._make_request("GET", api, params=params)

    def get_note_all_inner_comment(
        self, comment: Dict[str, Any], xsec_token: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """获取笔记的所有二级评论

        Args:
            comment: 一级评论对象
            xsec_token: 安全令牌

        Returns:
            元组 (success, message, comment): 包含所有二级评论的评论对象
        """
        try:
            if not comment.get("sub_comment_has_more", False):
                return True, "success", comment

            cursor = comment.get("sub_comment_cursor", "")
            inner_comment_list = []

            while True:
                success, msg, res_json = self.get_note_inner_comment(comment, cursor, xsec_token)
                if not success:
                    raise Exception(msg)

                comments = res_json.get("data", {}).get("comments", [])
                if "cursor" in res_json.get("data", {}):
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break

                inner_comment_list.extend(comments)

                if not res_json.get("data", {}).get("has_more", False):
                    break

            if "sub_comments" not in comment:
                comment["sub_comments"] = []
            comment["sub_comments"].extend(inner_comment_list)

        except Exception as e:
            return False, str(e), comment

        return True, "success", comment

    def get_note_all_comment(self, url: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取笔记的所有评论（包括一级和二级）

        Args:
            url: 笔记URL

        Returns:
            元组 (success, message, comment_list): 包含所有评论
        """
        out_comment_list = []

        try:
            url_parse = urllib.parse.urlparse(url)
            note_id = url_parse.path.split("/")[-1]
            kvs = url_parse.query.split("&") if url_parse.query else []
            kv_dict = {kv.split("=")[0]: kv.split("=")[1] for kv in kvs if "=" in kv}
            xsec_token = kv_dict.get("xsec_token", "")

            success, msg, out_comment_list = self.get_note_all_out_comment(note_id, xsec_token)
            if not success:
                raise Exception(msg)

            for comment in out_comment_list:
                success, msg, new_comment = self.get_note_all_inner_comment(comment, xsec_token)
                if not success:
                    raise Exception(msg)

        except Exception as e:
            return False, str(e), out_comment_list

        return True, "success", out_comment_list

    # ==================== 消息通知相关API ====================

    def get_unread_message(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取未读消息数量

        Returns:
            元组 (success, message, data): 包含未读消息信息
        """
        api = "/api/sns/web/unread_count"
        return self._make_request("GET", api)

    def get_mentions(self, cursor: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取评论和@提醒

        Args:
            cursor: 游标

        Returns:
            元组 (success, message, data): 包含提醒列表
        """
        api = "/api/sns/web/v1/you/mentions"
        params = {"num": "20", "cursor": cursor}
        return self._make_request("GET", api, params=params)

    def get_all_mentions(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取所有评论和@提醒

        Returns:
            元组 (success, message, mention_list): 包含所有提醒
        """
        cursor = ""
        mention_list = []

        try:
            while True:
                success, msg, res_json = self.get_mentions(cursor)
                if not success:
                    raise Exception(msg)

                mentions = res_json.get("data", {}).get("message_list", [])
                if "cursor" in res_json.get("data", {}):
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break

                mention_list.extend(mentions)

                if not res_json.get("data", {}).get("has_more", False):
                    break

        except Exception as e:
            return False, str(e), mention_list

        return True, "success", mention_list

    def get_likes_and_collects(self, cursor: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取赞和收藏通知

        Args:
            cursor: 游标

        Returns:
            元组 (success, message, data): 包含赞和收藏列表
        """
        api = "/api/sns/web/v1/you/likes"
        params = {"num": "20", "cursor": cursor}
        return self._make_request("GET", api, params=params)

    def get_all_likes_and_collects(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取所有赞和收藏通知

        Returns:
            元组 (success, message, like_list): 包含所有赞和收藏
        """
        cursor = ""
        like_list = []

        try:
            while True:
                success, msg, res_json = self.get_likes_and_collects(cursor)
                if not success:
                    raise Exception(msg)

                likes = res_json.get("data", {}).get("message_list", [])
                if "cursor" in res_json.get("data", {}):
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break

                like_list.extend(likes)

                if not res_json.get("data", {}).get("has_more", False):
                    break

        except Exception as e:
            return False, str(e), like_list

        return True, "success", like_list

    def get_new_connections(self, cursor: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取新增关注通知

        Args:
            cursor: 游标

        Returns:
            元组 (success, message, data): 包含新增关注列表
        """
        api = "/api/sns/web/v1/you/connections"
        params = {"num": "20", "cursor": cursor}
        return self._make_request("GET", api, params=params)

    def get_all_new_connections(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """获取所有新增关注通知

        Returns:
            元组 (success, message, connection_list): 包含所有新增关注
        """
        cursor = ""
        connection_list = []

        try:
            while True:
                success, msg, res_json = self.get_new_connections(cursor)
                if not success:
                    raise Exception(msg)

                connections = res_json.get("data", {}).get("message_list", [])
                if "cursor" in res_json.get("data", {}):
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break

                connection_list.extend(connections)

                if not res_json.get("data", {}).get("has_more", False):
                    break

        except Exception as e:
            return False, str(e), connection_list

        return True, "success", connection_list
