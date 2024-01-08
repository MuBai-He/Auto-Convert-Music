from os import popen, system
from time import sleep
from urllib.parse import quote
import requests
import sys
from pathlib import Path
import argparse

ipport = '127.0.0.1:8015'
site = f'http://{ipport}'

# 发送音频列表
def send_files_list(files_list):
    uri = quote(';'.join(files_list), encoding='utf8')
    r = requests.get(f'{site}/input?path={uri}')
    if r.ok:
        print(r.content.decode(encoding='utf8'))

# 选择输出路径
def select_output(t: str):
    r = requests.get(f'{site}/output/{t}')
    if r.ok:
        print(r.text)

def file_list():
    files = []
    for i in range(1, len(sys.argv)):
        p = Path(sys.argv[i])
        if p.exists() and p.is_file():
            files.append(str(p.resolve()))
    if not len(files):
        return
    send_files_list(files)

# 选择人声或伴奏
def select_stem(t):
    r = requests.get(f'{site}/select_stem/{t}')
    if r.ok:
        print(r.text)

def GPU_enable(t: bool):
    v = 1 if t else 0
    r = requests.get(f'{site}/GPU_enable/{v}')
    if r.ok:
        print(r.text)

# 选择模式
def select_method(t: str):
    tl = t.lower()
    t2 = tl[:2]
    model_type = ''
    if t2 in ('vr', 'md', 'de'):
        model_type = t2
    if not model_type:
        print('select_method/[vr|md|de]')
        return
    r = requests.get(f'{site}/select_method/{model_type}')
    if r.ok:
        print(r.text)

# 选择单个模型的json配置文件名，ultimatevocalremovergui\gui_data\saved_settings
def load_settings(t):
    if "Save Current Settings" == t:
        print("'Save Current Settings' is not support on web side")
        return
    r = requests.get(f'{site}/select_saved_settings/{t}')
    if r.ok:
        print(r.text)

# 选择多个模型的json配置文件名，ultimatevocalremovergui\gui_data\saved_ensembles
def load_ensemble_settings(t):
    r = requests.get(f'{site}/select_ensemble_settings/{t}')
    if r.ok:
        print(r.text)

def start_processing():
    r = requests.get(f'{site}/start_processing')
    if r.ok:
        print(r.text)

def ui_min():
    r = requests.get(f'{site}/ui_min')
    if r.ok:
        print(r.text)

def check_port_open() -> bool:
    return 'LISTENING' in popen(f'netstat -anp TCP|find "{ipport}"').read()

# 检测uvr5是否启动
def check_start_uvr5():
    if check_port_open():
        ui_min()
        return
    
    uvr5cmd = Path(__file__).parent.parent / "cmd" / "start_uvr5.cmd"
    if uvr5cmd.exists() and uvr5cmd.is_file():
        system(str(uvr5cmd))
        for _ in range(2):
            sleep(6)
            if check_port_open():
                ui_min()
                break
# 分离人声
def separation_song(input_file_path, output_folder, task_mode, config_name):
    check_start_uvr5()
    send_files_list((input_file_path,))
    select_output(output_folder)
    single_model = ['vr', 'md', 'de']
    if task_mode in single_model:
        select_method(task_mode)
        load_settings(config_name)
    else:
        select_method('mix')
        load_ensemble_settings(config_name)

    GPU_enable(True)
    select_stem('all')
    start_processing()

if __name__ == "__main__":
    '''# 示例
    check_start_uvr5()
    send_files_list((r'\audio\input\02mdx23c.wav',))
    select_output(r'\audio\output')

    # 单个模型
    # select_method('vr')
    # load_settings('Echo-Normal')

    # 多个模型
    select_method('mix')
    load_ensemble_settings('mix-1')
    GPU_enable(True)
    select_stem('all')
    start_processing()'''

    '''配置文件得自己在UI界面选择并配置。config即为配置文件名,不带后缀。'''
    parser = argparse.ArgumentParser(description='UVR5')
    parser.add_argument('-i', '--input_audio', type=str, help='input file path')
    parser.add_argument('-o', '--output_folder', type=str, help='output folder')
    parser.add_argument('-m', '--mode', type=str, help='task mode')
    parser.add_argument('-c', '--config', type=str, help='config name')

    args = parser.parse_args()
    separation_song(args.input, args.output, args.mode, args.config)
