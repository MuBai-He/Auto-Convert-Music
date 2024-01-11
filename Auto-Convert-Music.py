#coding=UTF-8
import subprocess
import threading
from send_uvr5cmd import *
import netease
import sys
from pathlib import Path
from pydub import AudioSegment
from pedalboard import Pedalboard,Compressor,NoiseGate,Gain,HighpassFilter
from pedalboard.io import AudioFile



class convert_music():
    def __init__(self):
        self.default_task_dict = {'en': 'mdx23c', 'vr1': '6-HP', 'vr2': 'De-Echo-Normal'}
        self.converting=[]
        self.converted=[]
        self.net_music = netease.Netease_music()

    def log_in_neteast(self):
        self.net_music.log_in()

    def download_music(self,music_name):
        name, file_path = self.net_music.search_download_music(music_name)
        return name,file_path
    
    def convert_music(self,music_name,vocal):

        thread = threading.Thread(target=self.convert_Netease,kwargs={'music_name': music_name, 'vocal': vocal})
        thread.start()

    def convert_Netease(self,music_name,vocal):
        name,file_path = self.download_music(music_name)
        self.converting.append(name)
        self.sep_song(song_name=name,file_path=file_path)
        self.convert_vocals(song_name=name,vocal=vocal)
        self.vocal_processing(song_name=name,vocal=vocal)
        self.mix_music(name,vocal)
        self.converting.pop(0)
        self.converted.append(name)

    def mix_music(self,song_name,vocal):
        Vocal = AudioSegment.from_wav(rf'output/{song_name}/Vocals_processed.wav')
        Background_music = AudioSegment.from_wav(rf'output/{song_name}/Instrumental.wav')
        Chord = AudioSegment.from_wav(rf'output/{song_name}/Chord.wav')
        Echo = AudioSegment.from_wav(rf'output/{song_name}/Echo.wav')

        output = Background_music.overlay(Vocal).overlay(Chord).overlay(Echo)
        output.export(f"output/{song_name}/{song_name}_{vocal}.wav", format="wav")

    def vocal_processing(self,song_name,vocal):
        board = Pedalboard(
            [NoiseGate(threshold_db=-15.0),Compressor(release_ms=150, attack_ms=5, threshold_db=3, ratio=3),
             HighpassFilter(cutoff_frequency_hz=110),
             Gain(gain_db=1)])

        vocal_path=fr"output/{song_name}/Vocals_{vocal}.wav"


        with AudioFile(vocal_path) as f:
            # Open an audio file to write to:
            with AudioFile(fr'output/{song_name}/Vocals_processed.wav', 'w', f.samplerate, f.num_channels) as o:
                # Read one second of audio at a time, until the file is empty:
                while f.tell() < f.frames:
                    chunk = f.read(f.samplerate)

                    # Run the audio through our pedalboard:
                    effected = board(chunk, f.samplerate, reset=False)

                    # Write the output to our output file:
                    o.write(effected)

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
    music_moudle.convert_Netease(music_name="17岁的歌",vocal="刻晴[中]")

