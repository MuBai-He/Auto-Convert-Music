# 参考：https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#embedding-yt-dlp
from yt_dlp import YoutubeDL
import os
import re
from loguru import logger

def search_youtube_video(keyword: str, max_results: int = 1) -> str:
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'playlistend': max_results,
    }
    key = f"{keyword} music"
    with YoutubeDL(ydl_opts) as ydl:
        search_query = f'ytsearch{max_results}:{key}'
        info = ydl.extract_info(search_query, download=False)
        
        video_links = [entry['url'] for entry in info['entries']]

    return video_links

def download_youtube_audio(url: str, output_path: str):
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path + r"\%(title)s.%(ext)s",
        'overwrites': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # 需要安装 ffmpeg !!!
            'preferredcodec': 'wav',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # print(info)

def download_music(music_info, output_path="./input", max_results=1, max_retry=5):
    file_existed_before_downloading = [i for i in os.listdir("input") 
                                       if re.search(r".mkv|.aac|.flac|.mp4|.mov|.wav", i)]
    if re.search(r"youtube.com/watch", music_info):
        music_url = music_info
    else:
        music_url = search_youtube_video(music_info, max_results)
        count = 0
        while not music_url:
            logger.warning("获取音乐URL失败，正在重试...")
            music_url = search_youtube_video(music_info, max_results)
            count += 1
            if count > max_retry:
                logger.error("获取音乐URL失败，已达到最大重试次数！请尝试更换平台或者关键词\
                             ！YouTube对各种语言的歌曲支持力度：英文>日文>其他语言(中文), 英文歌曲中关键词最好别出现其他语言，日文同理！否则会搜不到！")
                raise ValueError("获取音乐URL失败，已达到最大重试次数！请尝试更换平台或者关键词！")
            
        music_url = music_url[0]

    download_youtube_audio(music_url, output_path)
    file_existed_after_downloading = [i for i in os.listdir("input") 
                                      if re.search(r".mkv|.aac|.flac|.mp4|.mov|.wav", i)]
    music_file = list(set(file_existed_after_downloading) - set(file_existed_before_downloading))[0]
    music_file_new = re.sub(r"[&@#$%^【】。，、‘’：；“《》”？（）\s]+", "_", music_file)
    if not os.path.exists(f"input/{music_file_new}"):
        os.rename(f"input/{music_file}", f"input/{music_file_new}")
    music_file_name = music_file_new[:-4]
    music_file_path = os.path.join("input", music_file_new)
    return music_file_name, music_file_path


if __name__ == "__main__":
    music_info = "青柠 桃十五"    # 尽量加上歌手名，否则搜到的可能是其他的
    # music_info = "https://www.youtube.com/watch?v=BKblrXHumDk"
    print(download_music(music_info))