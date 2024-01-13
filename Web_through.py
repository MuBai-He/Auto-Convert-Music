#coding=UTF-8
import glob

from flask import Flask, jsonify, send_file,abort
from AutoConvertMusic import *

music_moudle = convert_music()
file_list=os.listdir("output\\")
converted_list={}

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def get_status():


    # 返回converting和converted的状态
    return jsonify({
        'converting': music_moudle.converting,
        'converted': music_moudle.converted,
        'converted_file': file_list
    })

@app.route('/append_song/<song_name>', methods=['POST'])
def convert_task(song_name):
    music_moudle.add_conversion_task(music_name=str(song_name),vocal="刻晴[中]")
    return music_moudle.converting

@app.route('/get_audio/<song_name>', methods=['GET'])
def get_audio(song_name):

    search_pattern = os.path.join(f"output\\{song_name}\\" + song_name + '*.wav')
    matching_files = glob.glob(search_pattern)[0]
    try:
        return send_file(matching_files, as_attachment=False)
    except:
        abort(404, description="Audio file not found")

if __name__ == '__main__':
    app.run(debug=True,port=1717)
