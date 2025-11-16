"""
数据处理器模块

负责处理和转换从API获取的原始数据，集成数据验证功能。
"""

import time
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger

from .validator import DataValidator, NoteData, UserInfo, CommentData


class DataProcessor:
    """数据处理器"""

    def __init__(self):
        """初始化数据处理器"""
        self.validator = DataValidator()

    @staticmethod
    def timestamp_to_str(timestamp: int) -> str:
        """
        将时间戳转换为字符串格式

        Args:
            timestamp: 毫秒级时间戳

        Returns:
            格式化的时间字符串 (YYYY-MM-DD HH:MM:SS)
        """
        time_local = time.localtime(timestamp / 1000)
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        return dt

    def handle_user_info(self, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """
        处理用户信息数据

        Args:
            data: 从API获取的原始用户数据
            user_id: 用户ID

        Returns:
            处理后的用户信息字典，验证失败返回None
        """
        try:
            home_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
            nickname = data["basic_info"]["nickname"]
            avatar = data["basic_info"]["imageb"]
            red_id = data["basic_info"]["red_id"]

            # 处理性别
            gender = data["basic_info"]["gender"]
            if gender == 0:
                gender = "男"
            elif gender == 1:
                gender = "女"
            else:
                gender = "未知"

            ip_location = data["basic_info"].get("ip_location", "未知")
            desc = data["basic_info"].get("desc", "")

            # 处理互动数据
            follows = data["interactions"][0]["count"]
            fans = data["interactions"][1]["count"]
            interaction = data["interactions"][2]["count"]

            # 处理标签
            tags_temp = data.get("tags", [])
            tags = []
            for tag in tags_temp:
                try:
                    tags.append(tag["name"])
                except (KeyError, TypeError):
                    pass

            user_info = {
                "user_id": user_id,
                "home_url": home_url,
                "nickname": nickname,
                "avatar": avatar,
                "red_id": red_id,
                "gender": gender,
                "ip_location": ip_location,
                "desc": desc,
                "follows": follows,
                "fans": fans,
                "interaction": interaction,
                "tags": tags,
            }

            # 验证数据
            validated_user = self.validator.validate_user(user_info)
            if validated_user:
                return user_info
            else:
                logger.error(f"User data validation failed for user_id: {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error processing user info for {user_id}: {e}")
            return None

    def handle_note_info(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理笔记信息数据

        Args:
            data: 从API获取的原始笔记数据

        Returns:
            处理后的笔记信息字典，验证失败返回None
        """
        try:
            note_id = data["id"]
            note_url = data["url"]

            # 处理笔记类型
            note_type = data["note_card"]["type"]
            if note_type == "normal":
                note_type = "图集"
            else:
                note_type = "视频"

            # 处理用户信息
            user_id = data["note_card"]["user"]["user_id"]
            home_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
            nickname = data["note_card"]["user"]["nickname"]
            avatar = data["note_card"]["user"]["avatar"]

            # 处理标题和描述
            title = data["note_card"]["title"]
            if title.strip() == "":
                title = "无标题"
            desc = data["note_card"].get("desc", "")

            # 处理互动数据
            interact_info = data["note_card"]["interact_info"]
            liked_count = interact_info.get("liked_count", 0)
            collected_count = interact_info.get("collected_count", 0)
            comment_count = interact_info.get("comment_count", 0)
            share_count = interact_info.get("share_count", 0)

            # 处理图片列表
            image_list_temp = data["note_card"].get("image_list", [])
            image_list = []
            for image in image_list_temp:
                try:
                    image_list.append(image["info_list"][1]["url"])
                except (KeyError, IndexError, TypeError):
                    pass

            # 处理视频信息
            if note_type == "视频":
                video_cover = image_list[0] if image_list else None
                try:
                    video_key = data["note_card"]["video"]["consumer"]["origin_video_key"]
                    video_addr = f"https://sns-video-bd.xhscdn.com/{video_key}"
                except (KeyError, TypeError):
                    video_addr = None
            else:
                video_cover = None
                video_addr = None

            # 处理标签
            tags_temp = data["note_card"].get("tag_list", [])
            tags = []
            for tag in tags_temp:
                try:
                    tags.append(tag["name"])
                except (KeyError, TypeError):
                    pass

            # 处理时间和位置
            upload_time = self.timestamp_to_str(data["note_card"]["time"])
            ip_location = data["note_card"].get("ip_location", "未知")

            note_info = {
                "note_id": note_id,
                "note_url": note_url,
                "note_type": note_type,
                "user_id": user_id,
                "home_url": home_url,
                "nickname": nickname,
                "avatar": avatar,
                "title": title,
                "desc": desc,
                "liked_count": liked_count,
                "collected_count": collected_count,
                "comment_count": comment_count,
                "share_count": share_count,
                "video_cover": video_cover,
                "video_addr": video_addr,
                "image_list": image_list,
                "tags": tags,
                "upload_time": upload_time,
                "ip_location": ip_location,
            }

            # 验证数据
            validated_note = self.validator.validate_note(note_info)
            if validated_note:
                return note_info
            else:
                logger.error(f"Note data validation failed for note_id: {note_id}")
                return None

        except Exception as e:
            logger.error(f"Error processing note info: {e}")
            logger.debug(f"Raw note data: {data}")
            return None

    def handle_comment_info(
        self, data: Dict[str, Any], note_id: str, note_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        处理评论信息数据

        Args:
            data: 从API获取的原始评论数据
            note_id: 笔记ID
            note_url: 笔记URL

        Returns:
            处理后的评论信息字典，验证失败返回None
        """
        try:
            comment_id = data["id"]
            user_id = data["user_info"]["user_id"]
            home_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
            nickname = data["user_info"]["nickname"]
            avatar = data["user_info"]["image"]
            content = data["content"]
            show_tags = data.get("show_tags", [])
            like_count = data.get("like_count", 0)
            upload_time = self.timestamp_to_str(data["create_time"])
            ip_location = data.get("ip_location", "未知")

            # 处理评论图片
            pictures = []
            try:
                pictures_temp = data.get("pictures", [])
                for picture in pictures_temp:
                    try:
                        pictures.append(picture["info_list"][1]["url"])
                    except (KeyError, IndexError, TypeError):
                        pass
            except (KeyError, TypeError):
                pass

            comment_info = {
                "note_id": note_id,
                "note_url": note_url,
                "comment_id": comment_id,
                "user_id": user_id,
                "home_url": home_url,
                "nickname": nickname,
                "avatar": avatar,
                "content": content,
                "show_tags": show_tags,
                "like_count": like_count,
                "upload_time": upload_time,
                "ip_location": ip_location,
                "pictures": pictures,
            }

            # 验证数据
            validated_comment = self.validator.validate_comment(comment_info)
            if validated_comment:
                return comment_info
            else:
                logger.error(f"Comment data validation failed for comment_id: {comment_id}")
                return None

        except Exception as e:
            logger.error(f"Error processing comment info: {e}")
            return None

    def batch_process_notes(self, notes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量处理笔记数据

        Args:
            notes_data: 原始笔记数据列表

        Returns:
            处理后的笔记数据列表（跳过验证失败的数据）
        """
        processed_notes = []
        for note_data in notes_data:
            processed = self.handle_note_info(note_data)
            if processed:
                processed_notes.append(processed)

        logger.info(f"Processed {len(processed_notes)}/{len(notes_data)} notes successfully")
        return processed_notes

    def batch_process_users(self, users_data: List[tuple]) -> List[Dict[str, Any]]:
        """
        批量处理用户数据

        Args:
            users_data: 原始用户数据列表，每项为 (data, user_id) 元组

        Returns:
            处理后的用户数据列表（跳过验证失败的数据）
        """
        processed_users = []
        for data, user_id in users_data:
            processed = self.handle_user_info(data, user_id)
            if processed:
                processed_users.append(processed)

        logger.info(f"Processed {len(processed_users)}/{len(users_data)} users successfully")
        return processed_users

    def batch_process_comments(self, comments_data: List[tuple]) -> List[Dict[str, Any]]:
        """
        批量处理评论数据

        Args:
            comments_data: 原始评论数据列表，每项为 (data, note_id, note_url) 元组

        Returns:
            处理后的评论数据列表（跳过验证失败的数据）
        """
        processed_comments = []
        for data, note_id, note_url in comments_data:
            processed = self.handle_comment_info(data, note_id, note_url)
            if processed:
                processed_comments.append(processed)

        logger.info(
            f"Processed {len(processed_comments)}/{len(comments_data)} comments successfully"
        )
        return processed_comments

    def save_note_detail(self, note: Dict[str, Any], path: str) -> None:
        """
        保存笔记详细信息到文本文件

        Args:
            note: 笔记信息字典
            path: 保存路径
        """
        detail_path = Path(path) / "detail.txt"
        detail_path.parent.mkdir(parents=True, exist_ok=True)

        with open(detail_path, mode="w", encoding="utf-8") as f:
            f.write(f"笔记id: {note['note_id']}\n")
            f.write(f"笔记url: {note['note_url']}\n")
            f.write(f"笔记类型: {note['note_type']}\n")
            f.write(f"用户id: {note['user_id']}\n")
            f.write(f"用户主页url: {note['home_url']}\n")
            f.write(f"昵称: {note['nickname']}\n")
            f.write(f"头像url: {note['avatar']}\n")
            f.write(f"标题: {note['title']}\n")
            f.write(f"描述: {note['desc']}\n")
            f.write(f"点赞数量: {note['liked_count']}\n")
            f.write(f"收藏数量: {note['collected_count']}\n")
            f.write(f"评论数量: {note['comment_count']}\n")
            f.write(f"分享数量: {note['share_count']}\n")
            f.write(f"视频封面url: {note['video_cover']}\n")
            f.write(f"视频地址url: {note['video_addr']}\n")
            f.write(f"图片地址url列表: {note['image_list']}\n")
            f.write(f"标签: {note['tags']}\n")
            f.write(f"上传时间: {note['upload_time']}\n")
            f.write(f"ip归属地: {note['ip_location']}\n")

        logger.debug(f"Note detail saved to {detail_path}")

    def save_user_detail(self, user: Dict[str, Any], path: str) -> None:
        """
        保存用户详细信息到文本文件

        Args:
            user: 用户信息字典
            path: 保存路径
        """
        detail_path = Path(path) / "detail.txt"
        detail_path.parent.mkdir(parents=True, exist_ok=True)

        with open(detail_path, mode="w", encoding="utf-8") as f:
            f.write(f"用户id: {user['user_id']}\n")
            f.write(f"用户主页url: {user['home_url']}\n")
            f.write(f"用户名: {user['nickname']}\n")
            f.write(f"头像url: {user['avatar']}\n")
            f.write(f"小红书号: {user['red_id']}\n")
            f.write(f"性别: {user['gender']}\n")
            f.write(f"ip地址: {user['ip_location']}\n")
            f.write(f"介绍: {user['desc']}\n")
            f.write(f"关注数量: {user['follows']}\n")
            f.write(f"粉丝数量: {user['fans']}\n")
            f.write(f"作品被赞和收藏数量: {user['interaction']}\n")
            f.write(f"标签: {user['tags']}\n")

        logger.debug(f"User detail saved to {detail_path}")

    def save_json(self, data: Dict[str, Any], filepath: str) -> None:
        """
        保存数据为JSON文件

        Args:
            data: 要保存的数据
            filepath: 文件路径
        """
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.debug(f"JSON data saved to {filepath}")
