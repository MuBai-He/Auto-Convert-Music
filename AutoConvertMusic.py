#coding=UTF-8
import queue
import re
import threading
import time
import traceback

from send_uvr5cmd import *
import netease
import bilibili
import sys
from pathlib import Path
from pydub import AudioSegment
from pedalboard import Pedalboard,Compressor,NoiseGate,Gain,HighpassFilter
from pedalboard.io import AudioFile
from logs import LogsBase
import importlib

my_logging=LogsBase(__name__)

class convert_music():

    os.makedirs("logs", exist_ok=True)
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    def __init__(self, music_platform : str,
                  svc_config : dict, 
                  default_task_dict={'en': 'mdx23c', 'vr1': '6-HP', 'vr2': 'De-Echo-Normal'}):
        self.default_task_dict = default_task_dict
        self.converting=[]
        self.converted=[]
        self.convertfail=[]
        self.waiting_queue = queue.Queue()
        self.music_platform = music_platform
        self.svc_config = svc_config
        if self.music_platform == "netease":
            self.net_music = netease.Netease_music()
        elif self.music_platform == "bilibili":
            self.bili_music = bilibili.Bilibili()
        elif self.music_platform == "youtube":
            self.youtube_music = importlib.import_module("youtube")
        else:
            raise ValueError("music_platform must be 'netease' or 'bilibili' or 'youtube'!")

    def add_conversion_task(self, music_info, speaker):

        find = False
        exist_files = [i for i in os.listdir("input") if re.search(r".mkv|.aac|.flac|.mp4|.ogg|.wav|.mp3", i)]
        for file in exist_files:
            if music_info in file:
                file_new_name = re.sub(r"[&@#$%^【】。，、‘’：；“《》”？（）\s]+", "_", file)
                if not os.path.exists(f"input/{file_new_name}"):
                    os.rename(f"input/{file}", f"input/{file_new_name}")
                song_name = file_new_name[:-4]
                music_file_path = f"input/{file_new_name}"
                find = True
                break

        if not find:
            if self.music_platform == "netease":
                id, song_name = self.net_music.search_music(song_name=music_info)
                song_name, music_file_path = self.net_music.download_music(id)
            elif self.music_platform == "bilibili":
                song_name, music_file_path=self.bili_music.download_music(music_info)
            elif self.music_platform == "youtube":
                song_name, music_file_path = self.youtube_music.search_download(music_info)

        if os.path.exists(f"output/{song_name}/{song_name}_{speaker}.wav")==True:
            self.converted.append(song_name)
            return "processed",song_name
        else:
            if len(self.converting)==0:
                self.converting.append(song_name)
                thread = threading.Thread(target=self.convert_music, kwargs={'name':song_name,'music_file_path': music_file_path, 'speaker': speaker})
                thread.start()
                return "processing",song_name
            else:
                self.waiting_queue.put((music_info, speaker))
                return "waiting",song_name

    def check_waiting_queue(self):
        if not self.waiting_queue.empty():
            music_info, speaker = self.waiting_queue.get()
            self.add_conversion_task(music_info, speaker)

    def convert_music(self,name, music_file_path, speaker):
        try:
            my_logging.info(f'开始转换歌曲:{name}')
            if not os.path.exists(f"output/{name}/Vocals.wav"):
                self.sep_song(song_name=name,file_path=music_file_path)
            my_logging.info(f'2.调用UVR分离声音：人声mdx23c->和声6-HP->混响De-Echo-Normal 完成:{name}')
            if not os.path.exists(f"output/{name}/Vocals_{speaker}.wav"):
                self.convert_vocals(song_name=name,speaker=speaker)
            my_logging.info(f'3.调用sovits4.1变声完成:{name}')
            self.vocal_processing(song_name=name,speaker=speaker)
            my_logging.info(f'4.音效处理完成:{name}')
            self.mix_music(name,speaker)
            my_logging.info(f'5.组合背景乐、和声完成:{name}')
            self.converting.remove(name)
            self.check_waiting_queue()
            self.converted.append(name)
            if name in self.convertfail:
                self.convertfail.remove(name)
            my_logging.info(f'歌曲完成转换:{name}')
        except Exception as e:
            win32gui.EnumWindows(self.close_window, None)
            traceback.print_exc()
            error=traceback.format_exc()
            my_logging.error(f'convert_music错误:{error}')
            if name in self.converting:
               self.converting.remove(name)
            self.convertfail.append(name)
            
    def close_window(self,hwnd,extra):
        if win32gui.IsWindowVisible(hwnd):
            if 'Ultimate Vocal Remover' in win32gui.GetWindowText(hwnd):
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    def mix_music(self,song_name,speaker):
        Vocal = AudioSegment.from_wav(rf'output/{song_name}/Vocals_processed.wav')
        Background_music = AudioSegment.from_wav(rf'output/{song_name}/Instrumental.wav')
        Chord = AudioSegment.from_wav(rf'output/{song_name}/Chord.wav')
        # Echo = AudioSegment.from_wav(rf'output/{song_name}/Echo.wav')

        output = Background_music.overlay(Vocal).overlay(Chord)#.overlay(Echo)
        output.export(f"output/{song_name}/{song_name}_{speaker}.wav", format="wav")

    def vocal_processing(self,song_name,speaker):
        board = Pedalboard(
            [Compressor(release_ms=150, attack_ms=5, threshold_db=3, ratio=3),
             HighpassFilter(cutoff_frequency_hz=110),
             Gain(gain_db=3)])

        vocal_path=fr"output/{song_name}/Vocals_{speaker}.wav"

        if os.path.exists(vocal_path):
            with AudioFile(vocal_path) as f:
                with AudioFile(fr'output/{song_name}/Vocals_processed.wav', 'w', f.samplerate, f.num_channels) as o:
                    chunk = f.read(f.frames)
                    effected = board(chunk, f.samplerate, reset=False)
                    o.write(effected)
            time.sleep(0.5)

    def convert_vocals(self,song_name, speaker):
        model_path = self.svc_config["model_path"]
        config_path = self.svc_config["config_path"]
        clean_names = f'./output/{song_name}/Vocals.wav'
        cluster_model_path = self.svc_config["cluster_model_path"]
        cluster_infer_ratio = self.svc_config["cluster_infer_ratio"]
        diffusion_model_path = self.svc_config["diffusion_model_path"]
        diffusion_config_path = self.svc_config["diffusion_config_path"]
        cmd = sys.executable + f" sovits4.1/inference_main.py -m {model_path} \
            -c {config_path} -n {clean_names} -s {speaker} \
            -cm {cluster_model_path} -cr {cluster_infer_ratio} \
            -dm {diffusion_model_path} -dc {diffusion_config_path}"
        
        subprocess.run(cmd, shell=True)

    def sep_song(self, song_name ,file_path):
        file_ex_path = os.getcwd()+"\\"+file_path
        output_path=os.getcwd()+ rf"\output\{song_name}"
        Path("./output", song_name).mkdir(parents=True, exist_ok=True)
        separation_song = Separation_Song(file_ex_path ,output_path , self.default_task_dict)
        separation_song.multi_model_order_separation()


if __name__ =="__main__":
    svc_config = {
        "model_path": r"sovits4.1\logs\44k\G_120000.pth",
        "config_path": r"sovits4.1\logs\44k\config.json",
        "cluster_model_path": r"sovits4.1\logs\44k\kmeans_10000.pt", # 这里填聚类模型的路径或特征索引文件的路径，如果没有就cluster_infer_ratio设置为 0
        "cluster_infer_ratio": 0.5, # 注意：如果没有聚类或特征索引文件，就设置为 0
        "diffusion_model_path": r"sovits4.1\logs\44k\diffusion\model_50000.pt",
        "diffusion_config_path": r"sovits4.1\logs\44k\diffusion\config.yaml"
    }
    choose_music_platform = ["netease", "bilibili", "youtube"]
    default_task_dict = {'en': 'mdx23c', 'vr1': '6-HP', 'vr2': 'De-Echo-Normal'}
    music_moudle=convert_music(music_platform="bilibili", svc_config=svc_config, default_task_dict=default_task_dict)
    music_moudle.add_conversion_task(music_info="Love Story Taylor Swift", speaker="神里绫华[中]")