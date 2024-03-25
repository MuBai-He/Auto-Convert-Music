#coding=UTF-8
import glob

from flask import Flask, jsonify, send_file,abort
from AutoConvertMusic import *

music_moudle = convert_music()
app = Flask(__name__)
vocal = "刻晴[中]"

@app.route('/musicInfo/<song_name>', methods=['GET'])
def get_music_info(song_name):
    id,song_name=music_moudle.music_info(song_name)
    return jsonify({"id": id, "songName": song_name})

@app.route('/status', methods=['GET'])
def get_status():
    vocal1 = vocal.replace("[中]", "[[]中[]]")
    file_list = glob.glob(f"output/*/*[!Vocals]*_{vocal1}.wav")
    file_name = []
    for f in file_list:
        filename = os.path.basename(f)
        file_name.append(filename.replace(f"_{vocal}.wav", ""))

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
    status,song_name=music_moudle.add_conversion_task(music_name=str(song_name),vocal="刻晴[中]")
    return jsonify({"status": status, "songName": song_name})

# 直接下载原始音乐
@app.route('/download_song/<song_name>', methods=['GET'])
def download_task(song_name):
    status,song_name=music_moudle.download_task(music_name=str(song_name))
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
