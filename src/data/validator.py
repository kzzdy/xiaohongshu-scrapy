"""
数据验证器模块

提供数据验证和清理功能，确保采集的数据完整性和合法性。
"""

import re
from typing import Optional, List, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl, field_validator
from loguru import logger


class UserInfo(BaseModel):
    """用户信息数据模型"""

    user_id: str = Field(..., description="用户ID")
    home_url: str = Field(..., description="用户主页URL")
    nickname: str = Field(..., description="用户昵称")
    avatar: str = Field(..., description="头像URL")
    red_id: str = Field(..., description="小红书号")
    gender: str = Field(..., description="性别")
    ip_location: str = Field(default="未知", description="IP归属地")
    desc: str = Field(default="", description="个人简介")
    follows: int = Field(default=0, ge=0, description="关注数量")
    fans: int = Field(default=0, ge=0, description="粉丝数量")
    interaction: int = Field(default=0, ge=0, description="获赞与收藏数量")
    tags: List[str] = Field(default_factory=list, description="用户标签")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """验证性别字段"""
        valid_genders = ["男", "女", "未知"]
        if v not in valid_genders:
            logger.warning(f"Invalid gender value: {v}, setting to '未知'")
            return "未知"
        return v


class NoteData(BaseModel):
    """笔记数据模型"""

    note_id: str = Field(..., description="笔记ID")
    note_url: str = Field(..., description="笔记URL")
    note_type: str = Field(..., description="笔记类型")
    user_id: str = Field(..., description="用户ID")
    home_url: str = Field(..., description="用户主页URL")
    nickname: str = Field(..., description="用户昵称")
    avatar: str = Field(..., description="头像URL")
    title: str = Field(..., description="笔记标题")
    desc: str = Field(default="", description="笔记描述")
    liked_count: int = Field(default=0, ge=0, description="点赞数量")
    collected_count: int = Field(default=0, ge=0, description="收藏数量")
    comment_count: int = Field(default=0, ge=0, description="评论数量")
    share_count: int = Field(default=0, ge=0, description="分享数量")
    video_cover: Optional[str] = Field(default=None, description="视频封面URL")
    video_addr: Optional[str] = Field(default=None, description="视频地址URL")
    image_list: List[str] = Field(default_factory=list, description="图片地址列表")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    upload_time: str = Field(..., description="上传时间")
    ip_location: str = Field(default="未知", description="IP归属地")

    @field_validator("note_type")
    @classmethod
    def validate_note_type(cls, v: str) -> str:
        """验证笔记类型"""
        valid_types = ["图集", "视频"]
        if v not in valid_types:
            raise ValueError(f"Invalid note type: {v}. Must be one of {valid_types}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """验证标题，空标题设置默认值"""
        if not v or v.strip() == "":
            return "无标题"
        return v


class CommentData(BaseModel):
    """评论数据模型"""

    note_id: str = Field(..., description="笔记ID")
    note_url: str = Field(..., description="笔记URL")
    comment_id: str = Field(..., description="评论ID")
    user_id: str = Field(..., description="用户ID")
    home_url: str = Field(..., description="用户主页URL")
    nickname: str = Field(..., description="用户昵称")
    avatar: str = Field(..., description="头像URL")
    content: str = Field(..., description="评论内容")
    show_tags: List[str] = Field(default_factory=list, description="评论标签")
    like_count: int = Field(default=0, ge=0, description="点赞数量")
    upload_time: str = Field(..., description="评论时间")
    ip_location: str = Field(default="未知", description="IP归属地")
    pictures: List[str] = Field(default_factory=list, description="评论图片列表")


class DataValidator:
    """数据验证器"""

    # 文件名非法字符正则表达式
    ILLEGAL_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\r\n]+')
    # Excel非法字符正则表达式
    ILLEGAL_EXCEL_CHARS = re.compile(r"[\000-\010]|[\013-\014]|[\016-\037]")

    @staticmethod
    def validate_note(data: Dict[str, Any]) -> Optional[NoteData]:
        """
        验证笔记数据

        Args:
            data: 原始笔记数据字典

        Returns:
            验证通过返回NoteData对象，失败返回None
        """
        try:
            note = NoteData(**data)
            logger.debug(f"Note data validated successfully: {note.note_id}")
            return note
        except Exception as e:
            logger.warning(f"Note data validation failed: {e}")
            logger.debug(f"Invalid note data: {data}")
            return None

    @staticmethod
    def validate_user(data: Dict[str, Any]) -> Optional[UserInfo]:
        """
        验证用户数据

        Args:
            data: 原始用户数据字典

        Returns:
            验证通过返回UserInfo对象，失败返回None
        """
        try:
            user = UserInfo(**data)
            logger.debug(f"User data validated successfully: {user.user_id}")
            return user
        except Exception as e:
            logger.warning(f"User data validation failed: {e}")
            logger.debug(f"Invalid user data: {data}")
            return None

    @staticmethod
    def validate_comment(data: Dict[str, Any]) -> Optional[CommentData]:
        """
        验证评论数据

        Args:
            data: 原始评论数据字典

        Returns:
            验证通过返回CommentData对象，失败返回None
        """
        try:
            comment = CommentData(**data)
            logger.debug(f"Comment data validated successfully: {comment.comment_id}")
            return comment
        except Exception as e:
            logger.warning(f"Comment data validation failed: {e}")
            logger.debug(f"Invalid comment data: {data}")
            return None

    @classmethod
    def clean_filename(cls, filename: str, max_length: int = 100) -> str:
        """
        清理文件名，移除非法字符

        Args:
            filename: 原始文件名
            max_length: 最大长度限制

        Returns:
            清理后的合法文件名
        """
        # 移除非法字符
        cleaned = cls.ILLEGAL_FILENAME_CHARS.sub("", filename)
        # 移除首尾空格
        cleaned = cleaned.strip()
        # 如果清理后为空，使用默认名称
        if not cleaned:
            cleaned = "untitled"
        # 限制长度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        return cleaned

    @classmethod
    def clean_text_for_excel(cls, text: str) -> str:
        """
        清理文本中的Excel非法字符

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not isinstance(text, str):
            text = str(text)
        return cls.ILLEGAL_EXCEL_CHARS.sub("", text)

    @staticmethod
    def check_file_exists(filepath: str) -> bool:
        """
        检查文件是否存在

        Args:
            filepath: 文件路径

        Returns:
            文件存在返回True，否则返回False
        """
        return Path(filepath).exists()

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL格式

        Args:
            url: URL字符串

        Returns:
            URL格式正确返回True，否则返回False
        """
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return url_pattern.match(url) is not None

    @staticmethod
    def validate_note_id(note_id: str) -> bool:
        """
        验证笔记ID格式

        Args:
            note_id: 笔记ID

        Returns:
            ID格式正确返回True，否则返回False
        """
        # 小红书笔记ID通常是24位十六进制字符
        return bool(re.match(r"^[a-f0-9]{24}$", note_id, re.IGNORECASE))

    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """
        验证用户ID格式

        Args:
            user_id: 用户ID

        Returns:
            ID格式正确返回True，否则返回False
        """
        # 小红书用户ID通常是24位十六进制字符
        return bool(re.match(r"^[a-f0-9]{24}$", user_id, re.IGNORECASE))
