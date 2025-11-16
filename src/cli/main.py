"""命令行界面主程序"""

import argparse
import sys
from typing import List, Optional
from pathlib import Path
from loguru import logger

from src.core.config import ConfigManager, ConfigError
from src.core.rate_limiter import RateLimiter
from src.core.error_handler import ErrorHandler
from src.core.progress import ProgressManager
from src.api.base import BaseAPIClient
from src.api.xhs_pc import XHSPCApi
from src.data.processor import DataProcessor
from src.data.exporter import DataExporter, ExportFormat
from src.spider.note_spider import NoteSpider
from src.spider.user_spider import UserSpider
from src.spider.search_spider import SearchSpider


class SpiderCLI:
    """爬虫命令行界面

    提供友好的命令行交互，支持：
    - 搜索笔记和用户
    - 爬取用户信息和笔记
    - 爬取指定笔记
    - 多种导出格式
    - 断点续传
    """

    def __init__(self):
        """初始化CLI"""
        self.parser = self._create_parser()
        self.config_manager = None
        self.config = None

    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器

        Returns:
            ArgumentParser: 参数解析器对象
        """
        parser = argparse.ArgumentParser(
            prog="xhs-spider",
            description="小红书爬虫工具 - 支持搜索、爬取笔记和用户信息",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  # 搜索笔记
  python -m src.cli.main search "美食" --num 10 --format excel
  
  # 爬取用户笔记
  python -m src.cli.main user <user_url> --format json --fetch-notes
  
  # 爬取指定笔记
  python -m src.cli.main note <note_url> --save-media
  
  # 显示帮助
  python -m src.cli.main --help
            """,
        )

        # 全局参数
        parser.add_argument("--config", type=str, default=".env", help="配置文件路径 (默认: .env)")

        parser.add_argument(
            "--log-level",
            type=str,
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="日志级别 (默认: INFO)",
        )

        # 创建子命令
        subparsers = parser.add_subparsers(
            dest="command",
            title="可用命令",
            description="选择要执行的操作",
            help="使用 '<command> --help' 查看详细帮助",
        )

        # 搜索命令
        self._add_search_parser(subparsers)

        # 用户命令
        self._add_user_parser(subparsers)

        # 笔记命令
        self._add_note_parser(subparsers)

        return parser

    def _add_search_parser(self, subparsers) -> None:
        """添加搜索命令解析器"""
        search_parser = subparsers.add_parser(
            "search", help="搜索笔记或用户", description="根据关键词搜索小红书笔记或用户"
        )

        search_parser.add_argument("query", type=str, help="搜索关键词")

        search_parser.add_argument(
            "--type",
            type=str,
            choices=["note", "user"],
            default="note",
            help="搜索类型 (默认: note)",
        )

        search_parser.add_argument("--num", type=int, default=20, help="需要的结果数量 (默认: 20)")

        search_parser.add_argument(
            "--sort",
            type=str,
            choices=["general", "time", "popularity", "comment", "collect"],
            default="general",
            help="排序方式 (默认: general) - 仅对笔记搜索有效",
        )

        search_parser.add_argument(
            "--note-type",
            type=str,
            choices=["all", "video", "normal"],
            default="all",
            help="笔记类型 (默认: all) - 仅对笔记搜索有效",
        )

        search_parser.add_argument(
            "--format",
            type=str,
            choices=["excel", "json", "csv"],
            default="excel",
            help="导出格式 (默认: excel)",
        )

        search_parser.add_argument(
            "--save-media", action="store_true", help="保存媒体文件（图片和视频）"
        )

        search_parser.add_argument("--no-export", action="store_true", help="不导出数据文件")

    def _add_user_parser(self, subparsers) -> None:
        """添加用户命令解析器"""
        user_parser = subparsers.add_parser(
            "user", help="爬取用户信息", description="爬取小红书用户信息和笔记"
        )

        user_parser.add_argument("url", type=str, help="用户主页URL")

        user_parser.add_argument("--fetch-notes", action="store_true", help="获取用户的所有笔记")

        user_parser.add_argument("--max-notes", type=int, help="最大笔记数量（不指定则获取全部）")

        user_parser.add_argument(
            "--format",
            type=str,
            choices=["excel", "json", "csv"],
            default="excel",
            help="导出格式 (默认: excel)",
        )

        user_parser.add_argument(
            "--save-media", action="store_true", help="保存媒体文件（图片和视频）"
        )

        user_parser.add_argument("--no-export", action="store_true", help="不导出数据文件")

    def _add_note_parser(self, subparsers) -> None:
        """添加笔记命令解析器"""
        note_parser = subparsers.add_parser(
            "note", help="爬取笔记信息", description="爬取小红书笔记信息和媒体文件"
        )

        note_parser.add_argument("url", type=str, nargs="+", help="笔记URL（可以指定多个）")

        note_parser.add_argument(
            "--save-media", action="store_true", help="保存媒体文件（图片和视频）"
        )

        note_parser.add_argument(
            "--format",
            type=str,
            choices=["excel", "json", "csv"],
            default="excel",
            help="导出格式 (默认: excel)",
        )

        note_parser.add_argument("--no-export", action="store_true", help="不导出数据文件")

        note_parser.add_argument(
            "--resume", action="store_true", help="启用断点续传（跳过已完成的笔记）"
        )

        note_parser.add_argument("--clear-progress", action="store_true", help="清除进度记录")

    def _setup_logging(self, log_level: str) -> None:
        """配置日志系统

        Args:
            log_level: 日志级别
        """
        # 移除默认的日志处理器
        logger.remove()

        # 添加控制台日志
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        )

        # 添加文件日志
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logger.add(
            log_dir / "spider_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )

        logger.add(
            log_dir / "error_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        )

    def _load_config(self, config_file: str) -> bool:
        """加载配置

        Args:
            config_file: 配置文件路径

        Returns:
            bool: 是否加载成功
        """
        try:
            self.config_manager = ConfigManager(config_file)
            self.config = self.config_manager.load_config()
            logger.info("配置加载成功")
            return True
        except ConfigError as e:
            logger.error(f"配置加载失败: {e}")
            return False
        except Exception as e:
            logger.error(f"配置加载异常: {e}")
            return False

    def _create_spider_components(self):
        """创建爬虫组件

        Returns:
            tuple: (note_spider, user_spider, search_spider)
        """
        # 创建核心组件
        rate_limiter = RateLimiter(rate=self.config.rate_limit)
        error_handler = ErrorHandler(logger)
        progress_manager = ProgressManager(self.config.progress_file)

        # 创建API客户端
        api_client = XHSPCApi(
            cookies=self.config.cookies,
            rate_limiter=rate_limiter,
            error_handler=error_handler,
            timeout=self.config.timeout,
            proxies=self.config.proxy,
        )

        # 创建数据处理组件
        data_processor = DataProcessor()
        data_exporter = DataExporter(output_dir=self.config.output_dir)

        # 创建爬虫
        note_spider = NoteSpider(
            api_client=api_client,
            progress_manager=progress_manager,
            data_processor=data_processor,
            data_exporter=data_exporter,
        )

        user_spider = UserSpider(
            api_client=api_client,
            data_processor=data_processor,
            data_exporter=data_exporter,
            note_spider=note_spider,
        )

        search_spider = SearchSpider(
            api_client=api_client,
            progress_manager=progress_manager,
            data_processor=data_processor,
            data_exporter=data_exporter,
            note_spider=note_spider,
        )

        return note_spider, user_spider, search_spider

    def run(self, args: Optional[List[str]] = None) -> int:
        """运行CLI

        Args:
            args: 命令行参数列表（可选，用于测试）

        Returns:
            int: 退出码（0表示成功，非0表示失败）
        """
        # 解析参数
        parsed_args = self.parser.parse_args(args)

        # 如果没有指定命令，显示帮助
        if not parsed_args.command:
            self.parser.print_help()
            return 0

        # 配置日志
        self._setup_logging(parsed_args.log_level)

        # 加载配置
        if not self._load_config(parsed_args.config):
            return 1

        # 创建爬虫组件
        try:
            note_spider, user_spider, search_spider = self._create_spider_components()
        except Exception as e:
            logger.error(f"创建爬虫组件失败: {e}")
            return 1

        # 执行命令
        try:
            if parsed_args.command == "search":
                return self.cmd_search(parsed_args, search_spider)
            elif parsed_args.command == "user":
                return self.cmd_user(parsed_args, user_spider)
            elif parsed_args.command == "note":
                return self.cmd_note(parsed_args, note_spider)
            else:
                logger.error(f"未知命令: {parsed_args.command}")
                return 1
        except KeyboardInterrupt:
            logger.warning("\n用户中断操作")
            return 130
        except Exception as e:
            logger.error(f"执行命令时发生错误: {e}", exc_info=True)
            return 1

    def cmd_search(self, args: argparse.Namespace, search_spider: SearchSpider) -> int:
        """搜索命令

        Args:
            args: 命令行参数
            search_spider: 搜索爬虫实例

        Returns:
            int: 退出码
        """
        logger.info(f"开始搜索: {args.query}")

        try:
            # 确定导出格式
            export_format = None
            if not args.no_export:
                format_map = {
                    "excel": ExportFormat.EXCEL,
                    "json": ExportFormat.JSON,
                    "csv": ExportFormat.CSV,
                }
                export_format = format_map.get(args.format)

            # 搜索笔记
            if args.type == "note":
                # 映射排序方式
                sort_map = {
                    "general": SearchSpider.SORT_GENERAL,
                    "time": SearchSpider.SORT_TIME,
                    "popularity": SearchSpider.SORT_POPULARITY,
                    "comment": SearchSpider.SORT_COMMENT,
                    "collect": SearchSpider.SORT_COLLECT,
                }
                sort_type = sort_map.get(args.sort, SearchSpider.SORT_GENERAL)

                # 映射笔记类型
                note_type_map = {
                    "all": SearchSpider.NOTE_TYPE_ALL,
                    "video": SearchSpider.NOTE_TYPE_VIDEO,
                    "normal": SearchSpider.NOTE_TYPE_NORMAL,
                }
                note_type = note_type_map.get(args.note_type, SearchSpider.NOTE_TYPE_ALL)

                # 执行搜索
                notes = search_spider.crawl_search_notes(
                    query=args.query,
                    num=args.num,
                    sort_type=sort_type,
                    note_type=note_type,
                    save_media=args.save_media,
                    export_format=export_format,
                )

                if notes:
                    logger.info(f"✓ 成功搜索到 {len(notes)} 条笔记")

                    # 显示统计信息
                    video_count = sum(1 for note in notes if note["note_type"] == "视频")
                    image_count = len(notes) - video_count
                    logger.info(f"  - 视频笔记: {video_count} 条")
                    logger.info(f"  - 图文笔记: {image_count} 条")

                    return 0
                else:
                    logger.warning("未找到任何笔记")
                    return 1

            # 搜索用户
            elif args.type == "user":
                users = search_spider.crawl_search_users(
                    query=args.query,
                    num=args.num,
                    export_format=export_format,
                )

                if users:
                    logger.info(f"✓ 成功搜索到 {len(users)} 个用户")

                    # 显示部分用户信息
                    for idx, user in enumerate(users[:5], 1):
                        logger.info(
                            f"  {idx}. {user['nickname']} (@{user['red_id']}) - 粉丝: {user['fans']}"
                        )

                    if len(users) > 5:
                        logger.info(f"  ... 还有 {len(users) - 5} 个用户")

                    return 0
                else:
                    logger.warning("未找到任何用户")
                    return 1

            else:
                logger.error(f"未知的搜索类型: {args.type}")
                return 1

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return 1

    def cmd_user(self, args: argparse.Namespace, user_spider: UserSpider) -> int:
        """用户命令

        Args:
            args: 命令行参数
            user_spider: 用户爬虫实例

        Returns:
            int: 退出码
        """
        logger.info(f"开始爬取用户: {args.url}")

        try:
            # 确定导出格式
            export_format = None
            if not args.no_export:
                format_map = {
                    "excel": ExportFormat.EXCEL,
                    "json": ExportFormat.JSON,
                    "csv": ExportFormat.CSV,
                }
                export_format = format_map.get(args.format)

            # 爬取用户信息
            result = user_spider.crawl_user(
                user_url=args.url,
                fetch_notes=args.fetch_notes,
                max_notes=args.max_notes,
                save_media=args.save_media,
                export_format=export_format,
            )

            if not result:
                logger.error("爬取用户信息失败")
                return 1

            # 显示用户信息
            user = result["user"]
            logger.info(f"✓ 成功爬取用户信息:")
            logger.info(f"  - 昵称: {user['nickname']}")
            logger.info(f"  - 小红书号: {user['red_id']}")
            logger.info(f"  - 粉丝数: {user['fans']}")
            logger.info(f"  - 关注数: {user['follows']}")
            logger.info(f"  - 获赞与收藏: {user['interaction']}")
            logger.info(f"  - IP属地: {user['ip_location']}")

            # 显示笔记信息
            if "notes" in result:
                notes = result["notes"]
                logger.info(f"✓ 成功爬取 {len(notes)} 条笔记")

                # 统计笔记类型
                video_count = sum(1 for note in notes if note["note_type"] == "视频")
                image_count = len(notes) - video_count
                logger.info(f"  - 视频笔记: {video_count} 条")
                logger.info(f"  - 图文笔记: {image_count} 条")

                # 统计互动数据
                total_likes = sum(note["liked_count"] for note in notes)
                total_collects = sum(note["collected_count"] for note in notes)
                total_comments = sum(note["comment_count"] for note in notes)
                logger.info(f"  - 总点赞数: {total_likes}")
                logger.info(f"  - 总收藏数: {total_collects}")
                logger.info(f"  - 总评论数: {total_comments}")

            return 0

        except Exception as e:
            logger.error(f"爬取用户信息失败: {e}")
            return 1

    def cmd_note(self, args: argparse.Namespace, note_spider: NoteSpider) -> int:
        """笔记命令

        Args:
            args: 命令行参数
            note_spider: 笔记爬虫实例

        Returns:
            int: 退出码
        """
        note_urls = args.url
        logger.info(f"开始爬取 {len(note_urls)} 条笔记")

        try:
            # 清除进度记录
            if args.clear_progress:
                note_spider.clear_progress()
                logger.info("已清除进度记录")

            # 显示进度统计
            if args.resume:
                stats = note_spider.get_progress_stats()
                if stats["completed_count"] > 0:
                    logger.info(f"断点续传已启用，已完成 {stats['completed_count']} 条笔记")

            # 确定导出格式
            export_format = None
            if not args.no_export:
                format_map = {
                    "excel": ExportFormat.EXCEL,
                    "json": ExportFormat.JSON,
                    "csv": ExportFormat.CSV,
                }
                export_format = format_map.get(args.format)

            # 单个笔记
            if len(note_urls) == 1:
                note = note_spider.crawl_note(
                    note_url=note_urls[0],
                    save_media=args.save_media,
                    export_format=export_format,
                )

                if not note:
                    logger.error("爬取笔记失败")
                    return 1

                # 显示笔记信息
                logger.info(f"✓ 成功爬取笔记:")
                logger.info(f"  - 标题: {note['title']}")
                logger.info(f"  - 作者: {note['nickname']}")
                logger.info(f"  - 类型: {note['note_type']}")
                logger.info(f"  - 点赞数: {note['liked_count']}")
                logger.info(f"  - 收藏数: {note['collected_count']}")
                logger.info(f"  - 评论数: {note['comment_count']}")

                if args.save_media:
                    if note["note_type"] == "视频":
                        logger.info(f"  - 已保存视频")
                    else:
                        logger.info(f"  - 已保存 {len(note['image_list'])} 张图片")

                return 0

            # 批量笔记
            else:
                notes = note_spider.crawl_notes(
                    note_urls=note_urls,
                    save_media=args.save_media,
                    export_format=export_format,
                    use_progress=args.resume,
                )

                if not notes:
                    logger.error("未能爬取任何笔记")
                    return 1

                # 显示统计信息
                logger.info(f"✓ 成功爬取 {len(notes)}/{len(note_urls)} 条笔记")

                # 统计笔记类型
                video_count = sum(1 for note in notes if note["note_type"] == "视频")
                image_count = len(notes) - video_count
                logger.info(f"  - 视频笔记: {video_count} 条")
                logger.info(f"  - 图文笔记: {image_count} 条")

                # 统计互动数据
                total_likes = sum(note["liked_count"] for note in notes)
                total_collects = sum(note["collected_count"] for note in notes)
                total_comments = sum(note["comment_count"] for note in notes)
                logger.info(f"  - 总点赞数: {total_likes}")
                logger.info(f"  - 总收藏数: {total_collects}")
                logger.info(f"  - 总评论数: {total_comments}")

                # 显示媒体文件统计
                if args.save_media:
                    total_images = sum(len(note["image_list"]) for note in notes)
                    logger.info(f"  - 已保存 {total_images} 张图片和 {video_count} 个视频")

                # 显示进度统计
                if args.resume:
                    stats = note_spider.get_progress_stats()
                    logger.info(f"  - 进度: {stats['completed_count']} 条已完成")

                return 0

        except Exception as e:
            logger.error(f"爬取笔记失败: {e}")
            return 1


def main():
    """主入口函数"""
    cli = SpiderCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
