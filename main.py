"""
Spider_XHS 主入口文件（兼容层）

⚠️ 注意：此文件保留用于向后兼容，建议使用新的模块化API。

新版本使用方式：
1. CLI方式：python -m src.cli.main search "关键词" --num 10
2. 代码方式：from src.spider.note_spider import NoteSpider

详见 MIGRATION.md 迁移指南
"""
import json
import os
import warnings
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.common_util import init
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx

# 显示弃用警告
warnings.filterwarnings('default', category=DeprecationWarning)

def _show_deprecation_warning():
    """显示弃用警告"""
    warning_msg = """
    ⚠️  弃用警告 (Deprecation Warning)
    
    你正在使用旧版本的API，虽然它仍然可以正常工作，但建议迁移到新的模块化架构。
    
    新版本提供：
    - ✅ 更好的错误处理和重试机制
    - ✅ 速率限制保护，避免被封禁
    - ✅ 断点续传功能
    - ✅ 多格式导出（JSON/CSV/Excel）
    - ✅ 命令行界面（CLI）
    - ✅ 环境变量配置管理
    
    迁移方式：
    1. 查看 MIGRATION.md 迁移指南
    2. 使用新CLI：python -m src.cli.main --help
    3. 使用新API：from src.spider.note_spider import NoteSpider
    
    如需继续使用旧版本，可忽略此警告。
    """
    warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)

# 在模块加载时显示一次警告
_show_deprecation_warning()


class Data_Spider():
    def __init__(self):
        self.xhs_apis = XHS_Apis()

    def spider_note(self, note_url: str, cookies_str: str, proxies=None):
        """
        爬取一个笔记的信息
        :param note_url:
        :param cookies_str:
        :return:
        """
        note_info = None
        try:
            success, msg, note_info = self.xhs_apis.get_note_info(note_url, cookies_str, proxies)
            if success:
                note_info = note_info['data']['items'][0]
                note_info['url'] = note_url
                note_info = handle_note_info(note_info)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取笔记信息 {note_url}: {success}, msg: {msg}')
        return success, msg, note_info

    def spider_some_note(self, notes: list, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一些笔记的信息
        :param notes:
        :param cookies_str:
        :param base_path:
        :return:
        """
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name 不能为空')
        note_list = []
        for note_url in notes:
            success, msg, note_info = self.spider_note(note_url, cookies_str, proxies)
            if note_info is not None and success:
                note_list.append(note_info)
        for note_info in note_list:
            if save_choice == 'all' or 'media' in save_choice:
                download_note(note_info, base_path['media'], save_choice)
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)


    def spider_user_all_note(self, user_url: str, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一个用户的所有笔记
        :param user_url:
        :param cookies_str:
        :param base_path:
        :return:
        """
        note_list = []
        success = False
        msg = "未知错误"
        try:
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies_str, proxies)
            if success:
                logger.info(f'用户 {user_url} 作品数量: {len(all_note_info)}')
                for simple_note_info in all_note_info:
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    note_list.append(note_url)
                if save_choice == 'all' or save_choice == 'excel':
                    excel_name = user_url.split('/')[-1].split('?')[0]
                self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
            else:
                logger.error(f'获取用户笔记列表失败: {msg}')
        except Exception as e:
            success = False
            msg = str(e)
            logger.error(f'爬取用户笔记异常: {msg}')
        logger.info(f'爬取用户所有视频 {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

    def spider_some_search_note(self, query: str, require_num: int, cookies_str: str, base_path: dict, save_choice: str, sort_type_choice=0, note_type=0, note_time=0, note_range=0, pos_distance=0, geo: dict = None,  excel_name: str = '', proxies=None):
        """
            指定数量搜索笔记，设置排序方式和笔记类型和笔记数量
            :param query 搜索的关键词
            :param require_num 搜索的数量
            :param cookies_str 你的cookies
            :param base_path 保存路径
            :param sort_type_choice 排序方式 0 综合排序, 1 最新, 2 最多点赞, 3 最多评论, 4 最多收藏
            :param note_type 笔记类型 0 不限, 1 视频笔记, 2 普通笔记
            :param note_time 笔记时间 0 不限, 1 一天内, 2 一周内天, 3 半年内
            :param note_range 笔记范围 0 不限, 1 已看过, 2 未看过, 3 已关注
            :param pos_distance 位置距离 0 不限, 1 同城, 2 附近 指定这个必须要指定 geo
            返回搜索的结果
        """
        note_list = []
        try:
            success, msg, notes = self.xhs_apis.search_some_note(query, require_num, cookies_str, sort_type_choice, note_type, note_time, note_range, pos_distance, geo, proxies)
            if success:
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                logger.info(f'搜索关键词 {query} 笔记数量: {len(notes)}')
                for note in notes:
                    note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = query
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'搜索关键词 {query} 笔记: {success}, msg: {msg}')
        return note_list, success, msg

if __name__ == '__main__':
    """
        此文件为爬虫的入口文件，可以直接运行
        apis/xhs_pc_apis.py 为爬虫的api文件，包含小红书的全部数据接口，可以继续封装
        apis/xhs_creator_apis.py 为小红书创作者中心的api文件
        
        ⚠️ 注意：建议使用新的CLI或模块化API
        
        新版本使用方式：
        1. CLI: python -m src.cli.main search "关键词" --num 10
        2. 代码: from src.spider.note_spider import NoteSpider
        
        详见 MIGRATION.md 迁移指南
        
        感谢star和follow
    """

    cookies_str, base_path = init()
    data_spider = Data_Spider()
    """
        save_choice: all: 保存所有的信息, media: 保存视频和图片（media-video只下载视频, media-image只下载图片，media都下载）, excel: 保存到excel
        save_choice 为 excel 或者 all 时，excel_name 不能为空
    """

    # ============================================
    # 以下是旧版API使用示例（仍然可用）
    # ============================================

    # 1 爬取列表的所有笔记信息 笔记链接 如下所示 注意此url会过期！
    notes = [
        r'https://www.xiaohongshu.com/explore/686e0c98000000001100265b?xsec_token=ABaDsc65cF-OUA2O_z-TLFpmmLMk0t9MKBgjkPLgkJcpw=',
    ]
    data_spider.spider_some_note(notes, cookies_str, base_path, 'all', 'test')

    # 2 爬取用户的所有笔记信息 用户链接 如下所示 注意此url会过期！
    user_url = 'https://www.xiaohongshu.com/user/profile/66630bea0000000007004016'
    # data_spider.spider_user_all_note(user_url, cookies_str, base_path, 'all')

    # 3 搜索指定关键词的笔记
    query = "重庆"
    query_num = 10
    sort_type_choice = 0  # 0 综合排序, 1 最新, 2 最多点赞, 3 最多评论, 4 最多收藏
    note_type = 0 # 0 不限, 1 视频笔记, 2 普通笔记
    note_time = 0  # 0 不限, 1 一天内, 2 一周内天, 3 半年内
    note_range = 0  # 0 不限, 1 已看过, 2 未看过, 3 已关注
    pos_distance = 0  # 0 不限, 1 同城, 2 附近 指定这个1或2必须要指定 geo
    # geo = {
    #     # 经纬度
    #     "latitude": 39.9725,
    #     "longitude": 116.4207
    # }
    # data_spider.spider_some_search_note(query, query_num, cookies_str, base_path, 'all', sort_type_choice, note_type, note_time, note_range, pos_distance, geo=None)
    
    # ============================================
    # 新版API使用示例（推荐）
    # ============================================
    """
    # 使用新版API的示例代码（取消注释以使用）
    
    from src.core.config import ConfigManager
    from src.spider.note_spider import NoteSpider
    from src.spider.user_spider import UserSpider
    from src.spider.search_spider import SearchSpider
    
    # 加载配置（从.env文件）
    config = ConfigManager().load_config()
    
    # 1. 爬取笔记
    note_spider = NoteSpider(config)
    note_info = note_spider.crawl_note(note_url)
    
    # 2. 爬取用户笔记
    user_spider = UserSpider(config)
    user_spider.crawl_user_notes(user_url, save_format="excel")
    
    # 3. 搜索笔记
    search_spider = SearchSpider(config)
    search_spider.search_notes("关键词", num=10, save_format="excel")
    
    # 或者使用CLI（更简单）：
    # python -m src.cli.main search "关键词" --num 10 --format excel
    """
