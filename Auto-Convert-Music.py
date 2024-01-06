import os
import subprocess
import requests
import sys

hd = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
}

python_v=sys.executable+" "
inference_base = f'inference.py'
inference_arg = f' --vocals_only true --large_gpu --use_VOCFT true'


class convert_music():
    def __init__(self):
        self.converting=[]
        self.converted=[]

    def convert_music_netease(self,id,name):
        self.converting.append(name)
        self.netease_download(id,name)

        self.converting.append(name)

    def convert_vocals(self,song_name, vocal):
        infer_vocals_end = f'./output/{song_name}/{song_name}_vocals.wav'
        convert_vocals = python_v + "./sovits4.1/inference_main.py " + f'-n {infer_vocals_end} -s {vocal}'
        subprocess.run(convert_vocals, shell=True)

    def netease_download(self,id, name):
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
    c.convert_vocals(song_name="Dacapo",vocal="刻晴[中]")
