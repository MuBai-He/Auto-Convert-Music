# 参考：https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#embedding-yt-dlp
from yt_dlp import YoutubeDL
import os
import re

def search_youtube_video(keyword: str, max_results: int = 1) -> list[str]:
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'playlistend': max_results,
    }
    key = f"{keyword} music"
    with YoutubeDL(ydl_opts) as ydl:
        search_query = f'ytsearch{max_results}:{key}'
        info = ydl.extract_info(search_query, download=False)
        
        video_links = [entry['url'] for entry in info['entries']]

    return video_links[0]

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

def search_download(music_info, output_path="./input", max_results=1):
    file_existed_before_downloading = [i for i in os.listdir("input") 
                                       if re.search(r".mkv|.aac|.flac|.mp4|.mov|.wav", i)]
    if re.search(r"youtube.com/watch", music_info):
        music_url = music_info
    else:
        music_url = search_youtube_video(music_info, max_results)
        while not music_url:
            print("获取音乐URL失败，正在重试...")
            music_url = search_youtube_video(music_info, max_results)

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
    music_info = "青柠 桃十五"    # 尽量加上歌手名，否则搜到的是其他的
    # music_info = "https://www.youtube.com/watch?v=BKblrXHumDk"
    print(search_download(music_info))