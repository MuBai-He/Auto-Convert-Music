# Part of the source code reference of Bilibili search song: https://github.com/DataWEIWEI/wei-tools/blob/main/Bilspider/AI_Spider1.py
# Thank you very much for the source code shared by this author!!!

import re
import time
import random
import traceback
from lxml import etree
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import subprocess
import sys
import os
from loguru import logger
os.environ["PYTHONIOENCODING"] = "UTF-8"

'''
综合排序&search_source=5
最多播放&search_source=5&order=click
最新发布&search_source=5&order=pubdate
最多弹幕&search_source=5&order=dm
最多收藏&search_source=5&order=stow

时长10分钟以下: &duration=1 10-30分钟: &duration=2  30-60分钟: &duration=3  60分钟以上: &duration=4
&tids=3 分区音乐
'''

def exception_capture(func):
    def work(*args, **kwargs):
        file = open("logs/bili.log", 'a', encoding='utf-8')
        try:
            res = func(*args, **kwargs)
            return res
        except Exception as e:
            traceback.print_exc(limit=None, file=file)
        file.close()

    return work


class BilVideoSpider(object):

    os.makedirs("logs", exist_ok=True)
    file = open("logs/bili.log", 'a', encoding='utf-8')

    def __init__(self,) -> None:
        self.tids = {'动画': 1,'音乐': 3,'舞蹈': 129,'游戏': 4,
                    '知识': 36,'科技': 188,'运动': 234,'生活': 160,
                    '时尚': 155,'娱乐': 5,'影视': 181,'全部': 0 }
        
        self.duration = {'0-10': 1,'10-30': 2,'30-60': 3,'60': 4}

    @exception_capture
    def get_search_html(self, url: str) -> str:
        options = Options()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = webdriver.Edge(options=options)
        driver.get(url)
        driver.refresh()
        time.sleep(random.randint(4, 6))

        html_str = driver.page_source
        driver.quit()

        return html_str

    @exception_capture
    def parse_search_html(self, html_str: str) -> list:
        parse_html = etree.HTML(html_str)
        e_list = parse_html.xpath(
            '//div[@class="bili-video-card__wrap __scale-wrap"]/a/@href')

        sub_url_list = []
        for i in e_list:
            sub_url_list.append(r'https:' + i)

        return sub_url_list

    @exception_capture
    def run(self, keyword: str, partition: str, duration: str, start: int, end: int) -> list:

        tid = self.tids[partition]
        which_duration = self.duration[duration]
        sub_url_lists = []

        for page in range(start, end + 1):
            logger.info('开始解析第{}页'.format(page))
            search_url = rf'https://search.bilibili.com/video?&keyword={keyword}&tids={tid}&page={page}&o={30*(page-1)}&duration={which_duration}'

            sub_url_list = self.parse_search_html(
                self.get_search_html(search_url))
            sub_url_lists.extend(sub_url_list)

            time.sleep(random.randint(2, 4))

        return sub_url_lists


class Bilibili:

    os.makedirs("input", exist_ok=True)

    def __init__(self,):
        self.bilibili_music_search = BilVideoSpider()

    def search_music(self, music_singer_name: str, max_retry:int = 5) -> str:
        music_template = "{} 音乐 歌曲 高音质 听歌 Hi-Res Hi-Fi 无损音质 百万级录音棚"
        keyword = music_template.format(music_singer_name)
        music_url_list = self.bilibili_music_search.run(keyword=keyword, partition="音乐", duration="0-10", start=1, end=1)
        count = 0
        while not music_url_list:
            logger.warning("获取音乐URL失败，正在重试...")
            music_url_list = self.bilibili_music_search.run(keyword=keyword, partition="音乐", duration="0-10", start=1, end=1)
            count += 1
            if count > max_retry:
                logger.error("获取音乐URL失败，已达到最大重试次数！请尝试更换平台或者关键词！ B站对各种语言的歌曲支持力度：中文>英文=日文>其他语言")
                raise ValueError("获取音乐URL失败，已达到最大重试次数！请尝试更换平台或者关键词！")

        return music_url_list[0]
    
    def download_music(self, music_info: str) -> str:
        file_existed_before_downloading = [i for i in os.listdir("input") if re.search(r".mkv|.aac|.flac|.mp4|.mov", i)]
        if re.search(r"video/BV|video/av|BV|av|play/ep|play/ss|media/md|ep|ss|md", music_info):
            music_url = music_info
        else:
            music_url = self.search_music(music_info)

        audio_format = "mkv"
        logger.success(f"开始下载音乐: {music_url}")
        cmd = sys.executable + f' -m yutto {music_url} --audio-only --output-format-audio-only {audio_format} -d "input" --no-danmaku'

        out = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8").stdout

        match = re.search("文件\s*(.*?)\s*已存在", out)
        if match:
            music_file = match.group(1)
            music_file_name = re.sub(r"[&@#$%^【】。，、‘’：；“《》”？（）\s]+", "_", music_file)
            if not os.path.exists(f"input/{music_file_name}.{audio_format}"):
                os.rename(f"input/{music_file}.{audio_format}", f"input/{music_file_name}.{audio_format}")
            music_file_path = f"input/{music_file_name}.{audio_format}"
            return music_file_name, music_file_path

        file_existed_after_downloading = [i for i in os.listdir("input") if re.search(r".mkv|.aac|.flac|.mp4|.mov", i)]
        music_file = list(set(file_existed_after_downloading) - set(file_existed_before_downloading))[0]

        music_file_new = re.sub(r"[&@#$%^【】。，、‘’：；“《》”？（）\s]+", "_", music_file)
        if not os.path.exists(f"input/{music_file_new}"):
            os.rename(f"input/{music_file}", f"input/{music_file_new}")
        music_file_name = music_file_new[:-4]
        music_file_path = os.path.join("input", music_file_new)
        return music_file_name, music_file_path

if __name__ == '__main__':
    music_info = "See The Fire In Your Eyes"
    music_info = "BV1Kg4y1F7qD"
    music_info = "https://www.bilibili.com/video/BV1Fj411P7zs"
    music_info = "ハロ／ハワユ 鹿乃"
    music_info = "璃月 陈致逸"
    music_info = "伊藤サチコ いつも何度でも"
    music_info = "https://www.bilibili.com/video/BV1ws411Y7wi/?spm_id_from=333.337.search-card.all.click"
    Bi = Bilibili()
    print(Bi.download_music(music_info= music_info))