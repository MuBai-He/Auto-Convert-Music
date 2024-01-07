from pydub import AudioSegment
from pydub.effects import

# 加载音频文件
audio = AudioSegment.from_file("input.wav", format="wav")

# 添加混响效果
reverbed_audio = reverb(audio, reverberance=50, decay=2, wet_gain=0)

# 导出混响后的音频文件
reverbed_audio.export("output.wav", format="wav")