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
        'converted_file': file_name
    })

@app.route('/append_song/<song_name>', methods=['GET'])
def convert_task(song_name):
    status,song_name=music_moudle.add_conversion_task(music_name=str(song_name),vocal="刻晴[中]")
    return jsonify({"status": status, "songName": song_name})

@app.route('/get_audio/<song_name>', methods=['GET'])
def get_audio(song_name):

    search_pattern = os.path.join(f"output\\{song_name}\\" + song_name + '*.wav')
    matching_files = glob.glob(search_pattern)[0]
    try:
        return send_file(matching_files, as_attachment=False)
    except:
        abort(404, description="Audio file not found")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1717)
