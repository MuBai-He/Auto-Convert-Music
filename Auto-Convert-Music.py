import subprocess
import threading

import netease
import sys
from pathlib import Path
from pydub import AudioSegment
from pedalboard import Pedalboard,Compressor,NoiseGate,HighShelfFilter,Gain,HighpassFilter
from pedalboard.io import AudioFile


class convert_music():
    def __init__(self):
        self.converting=[]
        self.converted=[]
    def convert_music(self,vocal,song_name,file):

        thread = threading.Thread(target=self.convert_file,kwargs={'file': file, 'song_name': song_name, 'vocal': vocal})
        thread.start()

    def convert_file(self,song_name,vocal,file):
        self.converting.append(song_name)
        self.sep_song(song_name=song_name,file_path=file)
        self.convert_vocals(song_name=song_name,vocal=vocal)
        self.vocal_processing(song_name=song_name,vocal=vocal,file=file)
        self.mix_music(song_name,vocal)
        self.converting.pop(0)
        self.converted.append(song_name)
    def mix_music(self,song_name,vocal):
        sound1 = AudioSegment.from_wav(rf'output/{song_name}/{song_name}_vocals_{vocal}_processed.wav')
        sound2 = AudioSegment.from_wav(rf'output/{song_name}/{song_name}_instrum.wav')

        output = sound1.overlay(sound2)  # 把sound2叠加到sound1上面
        output.export(f"output/{song_name}/{song_name}_{vocal}.wav", format="wav")  # 保存文件

    def vocal_processing(self,song_name,vocal,file=""):
        board = Pedalboard(
            [NoiseGate(threshold_db=-15.0),Compressor(release_ms=150, attack_ms=5, threshold_db=3, ratio=3),
             HighpassFilter(cutoff_frequency_hz=110),
             Gain(gain_db=1)])
        if file=="":
            vocal_path=fr"output/{song_name}/{song_name}_vocals_{vocal}.wav"
        else:
            vocal_path=file

        with AudioFile(vocal_path) as f:
            # Open an audio file to write to:
            with AudioFile(fr'output/{song_name}/{song_name}_vocals_{vocal}_processed.wav', 'w', f.samplerate, f.num_channels) as o:
                # Read one second of audio at a time, until the file is empty:
                while f.tell() < f.frames:
                    chunk = f.read(f.samplerate)

                    # Run the audio through our pedalboard:
                    effected = board(chunk, f.samplerate, reset=False)

                    # Write the output to our output file:
                    o.write(effected)
    def convert_vocals(self,song_name, vocal):
        infer_vocals_end = f'./output/{song_name}/{song_name}_vocals.wav'
        convert_vocals = sys.executable + " ./sovits4.1/inference_main.py " + f'-n "{infer_vocals_end}" -s {vocal}'
        subprocess.run(convert_vocals, shell=True)

    def sep_song(self, song_name ,file_path=""):
        Path('./output', song_name).mkdir(parents=True, exist_ok=True)

        if file_path == "":
            inference_task = sys.executable + ' ./send_uvr5cmd.py' + f' -i "input/{song_name}.mp3" -o "./output/{song_name}" -m mix -c mix-1'
        else:
            inference_task = sys.executable + ' ./send_uvr5cmd.py' + f' -i "{file_path}" -o "./output/{song_name}" -m mix -c mix-1'

        subprocess.run(inference_task, shell=True)


if __name__ =="__main__":
    net_music=netease.Netease_music()
    music_name=input("输入转换的歌曲")
    name, file_name=net_music.search_download_music(music_name)
    print(name,file_name)
