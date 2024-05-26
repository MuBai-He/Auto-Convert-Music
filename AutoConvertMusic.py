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
from pedalboard import Pedalboard,Compressor,NoiseGate,Gain,HighpassFilter,Reverb
from pedalboard.io import AudioFile
from logs import LogsBase
import importlib

my_logging=LogsBase(__name__)

input_path="G:\song\input"
save_path="G:\song\output"
class convert_music():

    os.makedirs("logs", exist_ok=True)
    os.makedirs(input_path, exist_ok=True)
    os.makedirs(save_path, exist_ok=True)

    def __init__(self, music_platform : str,
                  svc_config : dict, 
                  default_task_dict={'en': 'mdx23c', 'vr1': '6-HP', 'vr2': 'De-Echo-Normal'},
                  compress=False):
        self.default_task_dict = default_task_dict
        self.converting=[]
        self.converted=[]
        self.convertfail=[]
        self.waiting_queue = queue.Queue()
        self.music_platform = music_platform
        self.svc_config = svc_config
        self.compress = compress
        if self.music_platform == "netease":
            self.platform = netease.Netease_music()
        elif self.music_platform == "bilibili":
            self.platform = bilibili.Bilibili()
        elif self.music_platform == "youtube":
            self.platform = importlib.import_module("youtube")
        else:
            raise ValueError("music_platform must be 'netease' or 'bilibili' or 'youtube'!")
        self.search = netease.Netease_music()

    def add_conversion_task(self, music_info, speaker):

        # find = False
        # exist_files = [i for i in os.listdir("input") if re.search(r".mkv|.aac|.flac|.mp4|.ogg|.wav|.mp3", i)]
        # for file in exist_files:
        #     if music_info in file:
        #         file_new_name = re.sub(r"[&@#$%^【】。，、‘’：；“《》”？（）\s]+", "_", file)
        #         if not os.path.exists(f"input/{file_new_name}"):
        #             os.rename(f"input/{file}", f"input/{file_new_name}")
        #         song_name = file_new_name[:-4]
        #         music_file_path = f"input/{file_new_name}"
        #         find = True
        #         break

        # 搜索网络歌曲是否存在
        id,song_name=self.search.search_music(music_info)
        # 判断歌曲是否存在
        if os.path.exists(f"{save_path}/{song_name}/Vocals_processed.wav")==True and os.path.exists(f"{save_path}/{song_name}/accompany.wav")==True:
            self.converted.append(song_name)
            return "processed",song_name
        else:
            # 不存在下载歌曲
            song_name, music_file_path=self.platform.download_music(music_info)

            if len(self.converting)==0:
                self.converting.append(song_name)
                thread = threading.Thread(target=self.convert_music, 
                                          kwargs={'name':song_name,'music_file_path': music_file_path,
                                                   'speaker': speaker})
                thread.start()
                return "processing",song_name
            else:
                self.waiting_queue.put((music_info, speaker))
                return "waiting",song_name

    def download_task(self, music_name):
        #获取网易歌库歌曲名称
        id,song_name=self.platform.search_music(music_name)
        #判断歌曲是否生成
        if os.path.exists(f"{save_path}/{song_name}/{song_name}.wav")==True:
            self.converted.append(song_name)
            return "processed",song_name
        # 下载歌曲
        my_logging.info(f'开始下载歌曲:{music_name}')
        D_name,file_path = self.platform.download_path_music(id=id,download_folder=save_path)
        my_logging.info(f'1.下载歌曲完成:{music_name}')
        # 歌曲完成标志
        self.converted.append(music_name)
        if music_name in self.convertfail:
           self.convertfail.remove(music_name)
        my_logging.info(f'歌曲完成转换:{music_name}')
        return "processed",song_name
    
    def download_task_byid(self, id):
        #获取网易歌库歌曲名称
        id,song_name=self.platform.search_music_byid(id)
        #判断歌曲是否生成
        if os.path.exists(f"{save_path}/{song_name}/{song_name}.wav")==True:
            self.converted.append(song_name)
            return "processed",song_name
        # 下载歌曲
        my_logging.info(f'开始下载歌曲:{song_name}')
        D_name,file_path = self.platform.download_path_music(id=id,download_folder=save_path)
        my_logging.info(f'1.下载歌曲完成:{song_name}')
        # 歌曲完成标志
        self.converted.append(song_name)
        if song_name in self.convertfail:
           self.convertfail.remove(song_name)
        my_logging.info(f'歌曲完成转换:{song_name}')
        return "processed",song_name
    
    def check_waiting_queue(self):
        if not self.waiting_queue.empty():
            music_info, speaker = self.waiting_queue.get()
            self.add_conversion_task(music_info, speaker)

    def download_music(self,id):
        name,file_path = self.platform.download_music(id)
        return name,file_path
    
    def music_info(self,song_name):
        id,name=self.search.search_music(song_name)
        return id,name

    # 判断分离歌曲是否存在
    def sep_song_exists(self,name):
        Vocals = f"{save_path}/{name}/temp/Vocals.wav"
        Instrumental = f"{save_path}/temp/{name}/Instrumental.wav"
        Chord = f"{save_path}/{name}/temp/Chord.wav"
        Echo = f"{save_path}/{name}/temp/Echo.wav"
        if os.path.exists(Vocals) and os.path.exists(Instrumental) and os.path.exists(Chord) and os.path.exists(Echo):
            return True
        return False


    def convert_music(self,name, music_file_path, speaker):
        try:
            my_logging.info(f'开始转换歌曲:{name}')
            file_names = ["Vocals.wav", "Instrumental.wav", "Chord.wav", "Echo.wav"]
            # 1.调用UVR分离声音:人声、和声、混响
            if all([os.path.exists(f"{save_path}/{name}/{file_name}") for file_name in file_names])==False:
               self.sep_song(song_name=name,file_path=music_file_path)
            task = list(self.default_task_dict.values())
            my_logging.info(f'1-1.调用UVR分离声音：人声{task[0]}->和声{task[1]}->混响{task[2]} 完成:{name}')
            # 压缩音频
            if self.compress:
                # 压缩：压缩到指定路径
                if all([os.path.exists(f"{save_path}/{name}/{file_name}") for file_name in file_names])==False:
                   self.compressed_audio(name)
            else:
                # 不压缩：移动歌曲
                if all([os.path.exists(f"{save_path}/{name}/temp/{file_name}") for file_name in file_names]):
                    for file_name in file_names:
                        shutil.move(f"{save_path}/{name}/temp/{file_name}", f"{save_path}/{name}")
                    shutil.rmtree(f"{save_path}/{name}/temp")
            my_logging.info(f'1-2.压缩音频：人声->和声->混响 完成:{name}')
            # 2.调用sovits4.1变声完成
            if not os.path.exists(f"{save_path}/{name}/Vocals_{speaker}.wav"):
                self.convert_vocals(song_name=name,speaker=speaker)
            my_logging.info(f'2.调用sovits4.1变声完成:{name}')
            # 3.音效处理完成
            if not os.path.exists(f"{save_path}/{name}/Vocals_processed.wav"):
                self.vocal_processing(song_name=name,speaker=speaker)
            my_logging.info(f'3.音效处理完成:{name}')
            # 4.合成背景乐、和声
            # self.mix_music(name,speaker)
            # 4.合成伴奏
            if not os.path.exists(f"{save_path}/{name}/accompany.wav"):
               self.mix_music_accompany(name)
            my_logging.info(f'4.合成伴奏完成:{name}')
            # 队列调整
            self.converting.remove(name)
            # 转换失败，移除文件夹
            delete_filenames = ["Vocals.wav", "Instrumental.wav", "Chord.wav", "Echo.wav" , f"Vocals_{speaker}.wav"]
            if name in self.convertfail:
                self.convertfail.remove(name)
            else:
                self.converted.append(name)
                all([os.remove(f"{save_path}/{name}/{file_name}") for file_name in delete_filenames])

            my_logging.info(f'歌曲完成转换:{name}')
            #检查等待队列，调到下一首歌曲转换
            self.check_waiting_queue()
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

    def compressed_audio(self, name):
        Vocals = f"{save_path}/{name}/temp/Vocals.wav"
        if os.path.exists(Vocals):
            shutil.move(Vocals, f"{save_path}/{name}")
        Instrumental = f"{save_path}/{name}/temp/Instrumental.wav"
        Chord = f"{save_path}/{name}/temp/Chord.wav"
        Echo = f"{save_path}/{name}/temp/Echo.wav"
        if os.path.exists(Instrumental) and os.path.exists(Chord) and os.path.exists(Echo):
            for file in [Instrumental, Chord, Echo]:
                output_file = file.replace("temp/", "")
                cmd = f"ffmpeg -i \"{file}\" -ar 44100 -acodec pcm_s16le -ac 1 -y \"{output_file}\""
                print(cmd)
                subprocess.run(cmd ,shell=True)
            shutil.rmtree(f"{save_path}/{name}/temp")

    # 合成人声+伴奏【完整乐曲】
    def mix_music(self,song_name,speaker):
        Vocal = AudioSegment.from_wav(rf'{save_path}/{song_name}/Vocals_processed.wav')
        Background_music = AudioSegment.from_wav(rf'{save_path}/{song_name}/Instrumental.wav')
        Chord = AudioSegment.from_wav(rf'{save_path}/{song_name}/Chord.wav')
        # Echo = AudioSegment.from_wav(rf'{save_path}/{song_name}/Echo.wav')

        output = Background_music.overlay(Vocal).overlay(Chord)#.overlay(Echo)
        output.export(f"{save_path}/{song_name}/{song_name}_{speaker}.wav", format="wav")
    
    # 合成伴奏
    def mix_music_accompany(self,song_name):
        Background_music = AudioSegment.from_wav(rf'{save_path}/{song_name}/Instrumental.wav')
        Chord = AudioSegment.from_wav(rf'{save_path}/{song_name}/Chord.wav')

        output = Background_music.overlay(Chord)#.overlay(Echo)
        output.export(f"{save_path}/{song_name}/accompany.wav", format="wav")

    def vocal_processing(self,song_name,speaker):
        board = Pedalboard([
            Compressor(release_ms=150, attack_ms=5, threshold_db=3, ratio=3),
            HighpassFilter(cutoff_frequency_hz=110),
            Gain(gain_db=3),
            Reverb(room_size=0.22, damping=0.5, wet_level=0.22, dry_level=0.66, width=0.66)
        ])

        vocal_path=fr"{save_path}/{song_name}/Vocals_{speaker}.wav"

        if os.path.exists(vocal_path):
            with AudioFile(vocal_path) as f:
                with AudioFile(fr'{save_path}/{song_name}/Vocals_processed.wav', 'w', f.samplerate, f.num_channels) as o:
                    chunk = f.read(f.frames)
                    effected = board(chunk, f.samplerate, reset=False)
                    o.write(effected)
            time.sleep(0.5)

    def convert_vocals(self,song_name, speaker):
        model_path = self.svc_config["model_path"]
        config_path = self.svc_config["config_path"]
        clean_names = f'{save_path}/{song_name}/Vocals.wav'
        cluster_model_path = self.svc_config["cluster_model_path"]
        cluster_infer_ratio = self.svc_config["cluster_infer_ratio"]
        diffusion_model_path = self.svc_config["diffusion_model_path"]
        diffusion_config_path = self.svc_config["diffusion_config_path"]
        cmd = sys.executable + f" sovits4.1/inference_main.py -m \"{model_path}\" \
            -c \"{config_path}\" -n \"{clean_names}\" -s {speaker} \
            -cm \"{cluster_model_path}\" -cr {cluster_infer_ratio} \
            -dm \"{diffusion_model_path}\" -dc \"{diffusion_config_path}\""
        print(cmd)
        subprocess.run(cmd, shell=True)

    def sep_song(self, song_name ,file_path):
        output_path=f"{save_path}\{song_name}"
        Path(save_path, song_name).mkdir(parents=True, exist_ok=True)
        separation_song = Separation_Song(file_path ,output_path , self.default_task_dict)
        separation_song.multi_model_order_separation()


if __name__ == "__main__":
    svc_config = {
        "model_path": r"sovits4.1\logs\44k\G_120000.pth",
        "config_path": r"sovits4.1\logs\44k\config.json",
        "cluster_model_path": r"sovits4.1\logs\44k\kmeans_10000.pt", # 这里填聚类模型的路径或特征索引文件的路径，如果没有就cluster_infer_ratio设置为 0
        "cluster_infer_ratio": 0.5, # 注意：如果没有聚类或特征索引文件，就设置为 0
        "diffusion_model_path": r"sovits4.1\logs\44k\diffusion\model_50000.pt",
        "diffusion_config_path": r"sovits4.1\logs\44k\diffusion\config.yaml"
    }
    svc_config = {
        "model_path": r"sovits4.1\logs\44k-1\G_35000.pth",
        "config_path": r"sovits4.1\logs\44k-1\config.json",
        "cluster_model_path": r"sovits4.1\logs\44k-1\kmeans_10000.pt", # 这里填聚类模型的路径或特征索引文件的路径，如果没有就cluster_infer_ratio设置为 0
        "cluster_infer_ratio": 0, # 注意：如果没有聚类或特征索引文件，就设置为 0
        "diffusion_model_path": r"sovits4.1\logs\44k-1\diffusion\model_108000.pt",
        "diffusion_config_path": r"sovits4.1\logs\44k-1\diffusion\config.yaml"
    }
    choose_music_platform = ["netease", "bilibili", "youtube"]
    default_task_dict = {'en':'bs-roformer-1296','vr1':'6-HP','vr2': 'De-Echo-Normal'}  # 这是走UVR5的默认配置
    default_task_dict = {'ms':'bs-roformer-1296','vr1':'5-HP','vr2': 'De-Echo-Aggressive'}  # 这里ms会走Music-Source-Separation-Training
    music_moudle=convert_music(music_platform=choose_music_platform[0], svc_config=svc_config, default_task_dict=default_task_dict, compress=True)
    music_moudle.add_conversion_task(music_info="大喜 泠鸢", speaker="yousa")
    #music_moudle.add_conversion_task(music_info="罗刹海市", speaker="yousa")