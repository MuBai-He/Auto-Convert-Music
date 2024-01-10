from os import popen, system
from time import sleep
from urllib.parse import quote
import requests
import sys
from pathlib import Path
import argparse
import os
import shutil
import time
import loguru

class SendUvr5Config:
    def __init__(self, audio_format = 'WAV', device = True, select_stem = 'all', ui_min = True):
        self.ip_port = '127.0.0.1:8015'
        self.site = f'http://{self.ip_port}'
        self.audio_format = audio_format
        self.device = device
        self.select_stem = select_stem
        self.ui_min = ui_min

    # 发送输入的音频文件
    def send_input_file(self,select_input):
        uri = quote(';'.join(select_input), encoding='utf8')
        req = requests.get(f'{self.site}/input?path={uri}')
        if req.ok:
            print(req.content.decode(encoding='utf8'))
    
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
        req = requests.get(f'{self.site}/select_saved_settings/{model_config_name}')
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
        uvr5cmd = Path(__file__).parent.parent / "cmd" / "start_uvr5.cmd"
        if uvr5cmd.exists() and uvr5cmd.is_file():
            system(str(uvr5cmd))
            for _ in range(2):
                sleep(6)
                if self.check_port_open():
                    self.send_ui_min()
                    break


def single_model_separation(input_file_path, output_folder, task_mode, config_name = None, model_name = None):

    send_config.check_start_uvr5()
    send_config.send_input_file((input_file_path,))
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

    def get_all_file(self,file_path):
        file_list = []
        for root, dirs, files in os.walk(file_path):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    def delete_folder(self,file_path):
        folder_list = []
        for root, folders, files in os.walk(file_path):
            for folder in folders:
                folder_list.append(os.path.join(root, folder))
        shutil.rmtree(file_path)

    def check_file_exist(self,temp_folder, idx):
        # 1、分离人声和伴奏
        if idx == 0:
            wait_noise_file = True
            while wait_noise_file:
                file_list = self.get_all_file(temp_folder)
                for file in file_list:
                    if "Noise" in file:
                        time.sleep(1)
                        wait_noise_file = False

            for file in file_list:
                if "Vocals" in file:
                    shutil.copy(file, os.path.join(temp_folder, f"{idx}-v.wav")) # 0-v.wav 人声   mdx_model
                    self.input_file_path = os.path.join(temp_folder, f"{idx}-v.wav")  # 更改输入文件路径
                elif "Instrumental" in file:
                    shutil.copy(file, os.path.join(temp_folder, f"{idx}-i.wav")) # 0-i.wav 伴奏
            # self.delete_folder(temp_folder)

        # 2、去和声
        elif idx == 1:
            wait_vocals_file = True
            while wait_vocals_file:
                file_list = self.get_all_file(temp_folder)
                for file in file_list:
                    if "Vocals" in file:
                        time.sleep(1)
                        wait_noise_file = False

            for file in file_list:
                if "Vocals" in file:
                    os.rename(file, os.path.join(temp_folder, f"{idx}-v.wav"))
                    self.input_file_path = os.path.join(temp_folder, f"{idx}-v.wav")  # 更改输入文件路径
                elif "Instrumental" in file:
                    os.rename(file, os.path.join(temp_folder, f"{idx}-i.wav"))
        # 3、去混响
        elif idx == 2:
            wait_echo_file = True
            while wait_echo_file:
                file_list = self.get_all_file(temp_folder)
                for file in file_list:
                    if "Echo" in file:
                        time.sleep(1)
                        wait_echo_file = False

            for file in file_list:
                if "No" in file:
                    os.rename(file, os.path.join(temp_folder, f"{idx}-v.wav")) # 最终的人声

    def multi_model_order_separation(self,):
        for idx, task in enumerate(self.task_dict):
            single_model_separation(self.input_file_path, self.temp_folder, task, self.task_dict[task], None)
            self.check_file_exist(self.temp_folder, idx)
            loguru.logger.info(f"第{idx}个模型分离完成")

        shutil.copy(os.path.join(self.temp_folder, f"{idx}-v.wav"), os.path.join(self.output_folder, "vocals.wav"))
        time.sleep(1)
        # shutil.rmtree(self.temp_folder)

if __name__ == "__main__":
    '''配置文件得自己在UI界面选择并配置,config即为配置文件名,不带后缀。'''
    send_config = SendUvr5Config()

    default_task_dict = {'en':'KimV2','vr':'6-HP','vr': 'De-Echo-Normal'}
    parser = argparse.ArgumentParser(description='UVR5')
    parser.add_argument('-i', '--input_audio', type=str, help='input file path')
    parser.add_argument('-o', '--output_folder', type=str, help='output folder')
    parser.add_argument('-t', '--task_dict', default= default_task_dict, type=str, help='task dict')

    args = parser.parse_args()

    separation_song = Separation_Song(args.input_audio, args.output_folder, args.task_dict)
    separation_song.multi_model_order_separation()
    