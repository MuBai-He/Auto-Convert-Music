import os
import subprocess
import requests
import sys
from pathlib import Path


class convert_music():
    def __init__(self):
        self.converting=[]
        self.converted=[]

    def convert_music_netease(self,id,song_name,vocal):
        self.converting.append(song_name)
        self.netease_download(id=id,name=song_name)
        self.sep_song(song_name=song_name)
        self.convert_vocals(song_name=song_name,vocal=vocal)
        #处理

        self.converting.pop(0)
        self.converted.append(song_name)

    def convert_vocals(self,song_name, vocal):
        infer_vocals_end = f'./output/{song_name}/{song_name}_vocals.wav'
        convert_vocals = sys.executable + " ./sovits4.1/inference_main.py " + f'-n {infer_vocals_end} -s {vocal}'
        subprocess.run(convert_vocals, shell=True)

    def sep_song(self, song_name):
        Path('./output', song_name).mkdir(parents=True, exist_ok=True)
        inference_task = sys.executable + ' ./mdx23/inference.py' + f' --input_audio "input/{song_name}.mp3" --output_folder "./output/{song_name}"' + ' --vocals_only true'
        subprocess.run(inference_task, shell=True)
    def netease_download(self,id, name):
        hd = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        }
        if not os.path.exists('./input'):
            os.mkdir('./input')
        url = 'http://music.163.com/song/media/outer/url?id={}.mp3'
        r = requests.get(url.format(id), headers=hd)
        is_fail = False
        try:
            with open('./input/' + name + '.mp3', 'wb') as f:
                f.write(r.content)
        except:
            is_fail = True
            print("%s 下载出错" % name)
        if not is_fail:
            print("%s 下载完成" % name)

if __name__ =="__main__":
    c=convert_music()
    c.convert_music_netease(id=2094351580,song_name="命运之人",vocal="刻晴[中]")
