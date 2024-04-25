#coding=UTF-8
import glob
from flask import Flask, jsonify, send_file,abort
from AutoConvertMusic import *

svc_config = {
    "model_path": r"sovits4.1\logs\44k\G_120000.pth",
    "config_path": r"sovits4.1\logs\44k\config.json",
    "cluster_model_path": r"sovits4.1\logs\44k\kmeans_10000.pt", # 这里填聚类模型的路径或特征索引文件的路径，如果没有就cluster_infer_ratio设置为 0
    "cluster_infer_ratio": 0.5, # 注意：如果没有聚类或特征索引文件，就设置为 0
    "diffusion_model_path": r"sovits4.1\logs\44k\diffusion\model_50000.pt",
    "diffusion_config_path": r"sovits4.1\logs\44k\diffusion\config.yaml"
}

choose_music_platform = ["netease", "bilibili", "youtube"]
default_task_dict = {'en':'bs-roformer-1296','vr1':'6-HP','vr2': 'De-Echo-Normal'}  # 这是走UVR5的默认配置
default_task_dict = {'ms':'bs-roformer-1296','vr1':'6-HP','vr2': 'De-Echo-Normal'}  # 这里ms会走Music-Source-Separation-Training

music_moudle=convert_music(music_platform=choose_music_platform[0], svc_config=svc_config, default_task_dict=default_task_dict,compress=True)

app = Flask(__name__)
speaker = "刻晴[中]"


@app.route('/status', methods=['GET'])
def get_status():
    speaker1 = speaker.replace("[中]", "[[]中[]]")
    file_list = glob.glob(f"output/*/*[!Vocals]*_{speaker1}.wav")
    file_name = []
    for f in file_list:
        filename = os.path.basename(f)
        file_name.append(filename.replace(f"_{speaker}.wav", ""))

    # 返回converting和converted的状态
    return jsonify({
        'converting': music_moudle.converting,
        'converted': music_moudle.converted,
        'convertfail': music_moudle.convertfail,
        'converted_file': file_name
    })

# 音乐变声任务
@app.route('/append_song/<song_name>', methods=['GET'])
def convert_task(song_name):
    status,song_name = music_moudle.add_conversion_task(music_info=str(song_name), speaker=speaker)
    return jsonify({"status": status, "songName": song_name})

# 直接下载原始音乐
@app.route('/download_song/<song_name>', methods=['GET'])
def download_task(song_name):
    status,song_name=music_moudle.download_task(music_name=str(song_name), speaker=speaker)
    return jsonify({"status": status, "songName": song_name})

@app.route('/get_audio/<song_name>', methods=['GET'])
def get_audio(song_name):
    search_pattern = os.path.join(f"output/{song_name}/{song_name}*.wav")
    list = glob.glob(search_pattern)
    if len(list)>0:
        matching_files = list[0]
        try:
            return send_file(matching_files, as_attachment=False)
        except:
            abort(404, description="Audio file not found")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1717)
