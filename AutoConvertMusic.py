#coding=UTF-8
import queue
import re
import threading
import time
import traceback

from send_uvr5cmd import *
import netease
import sys
from pathlib import Path
from pydub import AudioSegment
from pedalboard import Pedalboard,Compressor,NoiseGate,Gain,HighpassFilter
from pedalboard.io import AudioFile
from logs import LogsBase

my_logging=LogsBase(__name__)

class convert_music():
    def __init__(self):
        self.default_task_dict = {'en': 'mdx23c', 'vr1': '6-HP', 'vr2': 'De-Echo-Normal'}
        self.converting=[]
        self.converted=[]
        self.convertfail=[]
        self.net_music = netease.Netease_music()
        self.waiting_queue = queue.Queue()

    def log_in_neteast(self):
        self.net_music.log_in()
    
    def add_conversion_task(self, music_name, vocal):
        #获取网易歌库歌曲名称
        id,song_name=self.music_info(song_name=music_name)
        #判断歌曲是否生成
        if os.path.exists(f"output/{song_name}/{song_name}_刻晴[中].wav")==True:
            self.converted.append(song_name)
            return "processed",song_name
        else:
            if len(self.converting)==0:
                self.converting.append(song_name)
                thread = threading.Thread(target=self.convert_music, kwargs={'name':song_name,'id': id, 'vocal': vocal})
                thread.start()
                return "processing",song_name
            else:
                self.waiting_queue.put((music_name, vocal))
                return "waiting",song_name

    def download_task(self, music_name):
        #获取网易歌库歌曲名称
        id,song_name=self.music_info(song_name=music_name)
        #判断歌曲是否生成
        if os.path.exists(f"output/{song_name}/{song_name}.wav")==True:
            self.converted.append(song_name)
            return "processed",song_name
        # 下载歌曲
        my_logging.info(f'开始下载歌曲:{music_name}')
        D_name,file_path = self.net_music.download_music(id=id,download_folder="output",vocal="刻晴[中]")
        my_logging.info(f'1.下载歌曲完成:{music_name}')
        # 歌曲完成标志
        self.converted.append(music_name)
        if music_name in self.convertfail:
           self.convertfail.remove(music_name)
        my_logging.info(f'歌曲完成转换:{music_name}')
        return "processed",song_name

    def check_waiting_queue(self):
        if not self.waiting_queue.empty():
            music_name, vocal = self.waiting_queue.get()
            self.add_conversion_task(music_name, vocal)

    def download_music(self,id):
        name,file_path = self.net_music.download_music(id)
        return name,file_path

    def music_info(self,song_name):
        id,name=self.net_music.search_music(song_name)
        #歌曲名称过滤
        name = re.sub(r'[\[\]<>:"/\\|?*]', '', name).rstrip('. ')
        return id,name

    def convert_music(self,name, id, vocal):
        try:
            my_logging.info(f'开始转换歌曲:{name}')
            D_name,file_path = self.download_music(id=id)
            my_logging.info(f'1.下载歌曲完成:{name}')
            self.sep_song(song_name=name,file_path=file_path)
            my_logging.info(f'2.调用UVR分离声音：人声mdx23c->和声6-HP->混响De-Echo-Normal 完成:{name}')
            self.convert_vocals(song_name=name,vocal=vocal)
            my_logging.info(f'3.调用sovits4.1变声完成:{name}')
            self.vocal_processing(song_name=name,vocal=vocal)
            my_logging.info(f'4.压缩器，高通滤波，增益等音效处理完成:{name}')
            self.mix_music(name,vocal)
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


    def mix_music(self,song_name,vocal):
        Vocal = AudioSegment.from_wav(rf'output/{song_name}/Vocals_processed.wav')
        Background_music = AudioSegment.from_wav(rf'output/{song_name}/Instrumental.wav')
        Chord = AudioSegment.from_wav(rf'output/{song_name}/Chord.wav')
        Echo = AudioSegment.from_wav(rf'output/{song_name}/Echo.wav')

        output = Background_music.overlay(Vocal).overlay(Chord).overlay(Echo)
        output.export(f"output/{song_name}/{song_name}_{vocal}.wav", format="wav")

    def vocal_processing(self,song_name,vocal):
        board = Pedalboard(
            [Compressor(release_ms=150, attack_ms=5, threshold_db=3, ratio=3),
             HighpassFilter(cutoff_frequency_hz=110),
             Gain(gain_db=3)])

        vocal_path=fr"output/{song_name}/Vocals_{vocal}.wav"


        for i in range(10):
            if os.path.exists(vocal_path):
                with AudioFile(vocal_path) as f:
                    # Open an audio file to write to:
                    with AudioFile(fr'output/{song_name}/Vocals_processed.wav', 'w', f.samplerate, f.num_channels) as o:
                        # Read one second of audio at a time, until the file is empty:
                        while f.tell() < f.frames:
                            chunk = f.read(f.samplerate)
                            
                            # TODO：只因你太美 (Live) 转换错误，这里加一个try catch
                            # Run the audio through our pedalboard:
                            effected = board(chunk, f.samplerate, reset=False)

                            # Write the output to our output file:
                            o.write(effected)
                            
                break
            time.sleep(0.5)

    def convert_vocals(self,song_name, vocal):
        infer_vocals_end = f'./output/{song_name}/Vocals.wav'
        convert_vocals = sys.executable + " ./sovits4.1/inference_main.py " + f'-n "{infer_vocals_end}" -s {vocal}'
        subprocess.run(convert_vocals, shell=True)

    def sep_song(self, song_name ,file_path):
        file_ex_path = os.getcwd()+"\\"+file_path
        output_path=os.getcwd()+ rf"\output\{song_name}"
        Path("./output", song_name).mkdir(parents=True, exist_ok=True)
        separation_song = Separation_Song(file_ex_path ,output_path , self.default_task_dict)
        separation_song.multi_model_order_separation()

if __name__ =="__main__":
    music_moudle=convert_music()
    music_moudle.add_conversion_task(music_name="運命の人 『ユイカ』", vocal="刻晴[中]")

