from pydub import AudioSegment
from pydub.effects import

# ������Ƶ�ļ�
audio = AudioSegment.from_file("input.wav", format="wav")

# ��ӻ���Ч��
reverbed_audio = reverb(audio, reverberance=50, decay=2, wet_gain=0)

# ������������Ƶ�ļ�
reverbed_audio.export("output.wav", format="wav")