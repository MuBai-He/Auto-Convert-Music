import subprocess
from os import popen, system
from time import sleep
from urllib.parse import quote
import requests
import sys
import win32gui
from win32.lib import win32con
from pathlib import Path
import argparse
import os
import shutil
import time
import json
import loguru

class SendUvr5Config:
    def __init__(self, audio_format = 'WAV', device = True, select_stem = 'all', ui_min = True):
        self.ip_port = '127.0.0.1:8015'
        self.site = f'http://{self.ip_port}'
        self.audio_format = audio_format
        self.device = device
        self.select_stem = select_stem
        self.ui_min = ui_min
        self.UVR_PID = None

    # 发送输入的音频文件
    def send_input_file(self,select_input):
        uri = quote(';'.join(select_input), encoding='utf8')
        req = requests.get(f'{self.site}/input?path={uri}')
        if req.ok:
            print(req.content.decode(encoding='utf8'))
            return req.content.decode(encoding='utf8')
    
    # 选择输出路径
    def send_output_folder(self,select_output):
        req = requests.get(f'{self.site}/output/{select_output}')
        if req.ok:
            print(req.text)

    # 选择模式['vr', 'md', 'de' ,'en']
    def send_choose_process_method(self,choose_process_method: str):
        choose_process_method = choose_process_method.lower()
        req = requests.get(f'{self.site}/select_method/{choose_process_method}')
        if req.ok:
            print(req.text)

    # 选择单个模型，模式选择 ['vr', 'md', 'de' ] 选择单个模型名字，路径ultimatevocalremovergui\models下的模型名字
    def send_choose_single_model(self,choose_single_model_mothod: str):
        req = requests.get(f'{self.site}/select_single_model/{choose_single_model_mothod}')
        if req.ok:
            print(req.text)

    # # 音频格式，wav、flac、mp3, 默认wav
    # def send_audio_format(self):
    #     req = requests.get(f'{self.site}/select_audio_format/{self.audio_format}')
    #     if req.ok:
    #         print(req.text)
    
    # 是否使用GPU,默认 True 
    def send_device(self):
        req = requests.get(f'{self.site}/select_device/{self.device}')
        if req.ok:
            print(req.text)

    # 选择人声、伴奏、全部 ["vo","in","all"] 目前不支持某些模型设置 Echo or No Echo, 建议选择all
    def send_select_stem(self):
        req = requests.get(f'{self.site}/select_stem/{self.select_stem}')
        if req.ok:
            print(req.text)

    # 最小化界面
    def send_ui_min(self):
        req = requests.get(f'{self.site}/ui_min')
        if req.ok:
            print(req.text)

    # 配置文件得自己在UI界面选择并配置。不带json后缀配置文件名
    # 加载单个模型的配置,模式选择 ['vr', 'md', 'de' ]选择单个模型的json配置文件名，ultimatevocalremovergui\gui_data\saved_settings
    def load_saved_settings(self,model_config_name):
        req = requests.get(f'{self.site}/select_saved_setting/{model_config_name}')
        if req.ok:
            print(req.text)

    # 加载多个模型的配置,模式选择 "en" 选择多个模型的json配置文件名，ultimatevocalremovergui\gui_data\saved_ensembles
    def load_ensemble_settings(self,ensemble_config_name):
        req = requests.get(f'{self.site}/select_ensemble_settings/{ensemble_config_name}')
        if req.ok:
            print(req.text)

    # 开始推理
    def start_processing(self):
        req = requests.get(f'{self.site}/start_processing')
        if req.ok:
            print(req.text)

    def check_port_open(self) -> bool:
        return 'LISTENING' in popen(f'netstat -anp TCP|find "{self.ip_port}"').read()
    
    # 检测uvr5是否启动
    def check_start_uvr5(self):
        if self.check_port_open():
            self.send_ui_min()
            return
        uvr5 = sys.executable + " ultimatevocalremovergui/UVR.py"
        process = subprocess.Popen(uvr5, shell=True)
        self.UVR_PID = process.pid
        while True:
            if self.check_port_open():
                self.send_ui_min()
                break
            sleep(1)

send_config = SendUvr5Config()

def single_model_separation(input_file_path, output_folder, task_mode, config_name = None, model_name = None):
    send_config.check_start_uvr5()
    while True:
        test_busy = send_config.send_input_file((input_file_path,))
        if "tootoobusy" not in test_busy:
            break
        time.sleep(1)

    send_config.send_output_folder(output_folder)
    send_config.send_choose_process_method(task_mode)

    if config_name and model_name is None: 
        if task_mode == 'en':
            send_config.load_ensemble_settings(config_name)
        elif task_mode in ['vr', 'md', 'de']:
            send_config.load_saved_settings(config_name)

    elif model_name and config_name is None:
        send_config.send_choose_single_model(model_name+"|"+task_mode)

    # send_config.send_audio_format()
    send_config.send_device()
    send_config.send_select_stem()
    send_config.start_processing()


class Separation_Song:
    def __init__(self, input_file_path, output_folder, task_dict):
        self.input_file_path = input_file_path
        self.temp_folder = os.path.join(output_folder, "temp")
        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)
        self.output_folder = output_folder
        self.task_dict = task_dict
        self.keys_list = list(self.task_dict.keys())
        self.values_list = list(self.task_dict.values())

    def get_model_name(self,idx):
        if self.keys_list[idx].lower()[:2] == 'en':
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultimatevocalremovergui\gui_data\saved_ensembles", self.values_list[idx]+".json")
        else:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultimatevocalremovergui\gui_data\saved_settings", self.values_list[idx]+".json")
        with open(config_path, 'r') as f:
            config = json.load(f)
            if self.keys_list[idx].lower()[:2] == 'en':
                model_name = config["selected_models"]
            else:
                model_name = list(config.values())[0]
        return model_name
        
    def wait_finish_inference(self,idx):
        model_name = str(self.get_model_name(idx)).lower()
        need_test_file = ["No","Echo"] if "echo" in model_name else ["Vocals", "Instrumental"]
        while True:
            file_list = os.listdir(self.temp_folder)
            for file in file_list:
                if need_test_file[0] in file:
                    time.sleep(4)
                    return  need_test_file

    def close_window(self,hwnd,extra):
        if win32gui.IsWindowVisible(hwnd):

            if 'Ultimate Vocal Remover' in win32gui.GetWindowText(hwnd):
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    def rename_file(self, need_rename, temp_folder, idx):
        for file in os.listdir(temp_folder):
            if need_rename[0] in file:
                os.rename(os.path.join(temp_folder, file), os.path.join(temp_folder, f"{idx}-v.wav"))
                self.input_file_path = os.path.join(temp_folder, f"{idx}-v.wav")

            elif need_rename[1] in file:
                os.rename(os.path.join(temp_folder, file), os.path.join(temp_folder, f"{idx}-i.wav"))

    def check_file_exist(self, temp_folder, idx):
        need_rename = self.wait_finish_inference(idx)
        while True:
            self.rename_file(need_rename, temp_folder, idx)
            if os.path.exists(os.path.join(temp_folder, f"{idx}-v.wav")) and os.path.exists(os.path.join(temp_folder, f"{idx}-i.wav")):
                break
            time.sleep(1)

    def multi_model_order_separation(self,):
        for idx, task in enumerate(self.task_dict):
            loguru.logger.info(f"开始第{idx}个模型分离,模型任务为：{self.task_dict[task]}")
            single_model_separation(self.input_file_path, self.temp_folder, task.lower()[:2], self.task_dict[task], None)
            self.check_file_exist(self.temp_folder, idx)
            loguru.logger.success(f"第{idx}个模型分离完成")

        shutil.copy(os.path.join(self.temp_folder, f"{idx}-v.wav"), os.path.join(self.output_folder, "Vocals.wav"))  # 经过多个模型分离的人声文件
        shutil.copy(os.path.join(self.temp_folder, "0-i.wav"), os.path.join(self.output_folder, "Instrumental.wav"))    # 第一个MDX分离的伴奏文件
        shutil.copy(os.path.join(self.temp_folder, f"{idx-1}-i.wav"), os.path.join(self.output_folder, "Chord.wav"))    # 和声
        shutil.copy(os.path.join(self.temp_folder, f"{idx}-i.wav"), os.path.join(self.output_folder, "Echo.wav"))       # 混响

        time.sleep(1)
        shutil.rmtree(self.temp_folder)     # 删除临时文件夹
        win32gui.EnumWindows(self.close_window, None)

if __name__ == "__main__":
    '''目前尚未解决指定模型名推理的问题,只能使用配置文件推理.
    mdx系列只能配置Ensemble模式, 在MDX模式下配置,保存后的配置文件中的模型名并不是你选择的。VR系列可以在VR模式下配置
    配置文件得自己在UI界面选择并配置,config即为配置文件名,不带后缀。'''

    default_task_dict = {'en':'mdx23c','vr1':'6-HP','vr2': 'De-Echo-Normal'} # 在这里配置模型任务,相同的模式要加上数字区分
    parser = argparse.ArgumentParser(description='UVR5')
    parser.add_argument('-i', '--input_audio', type=str, help='input file path')    # 音频文件的绝对路径
    parser.add_argument('-o', '--output_folder', type=str, help='output folder')    # 输出文件夹的绝对路径
    args = parser.parse_args()

    separation_song = Separation_Song(args.input_audio, args.output_folder, default_task_dict)
    # separation_song = Separation_Song(r"D:\Project\test_uvr5\audio\input\lovely.mp3", r"D:\Project\test_uvr5\audio\output", default_task_dict)
    separation_song.multi_model_order_separation()

    # 运行完成后，输出文件夹中会有两个文件，Vocals.wav为人声，Instrumental.wav为伴奏，temp文件夹为临时文件夹，会自动删除
    # python send_uvr5cmd.py -i "D:\test\test.wav" -o "D:\test\test"