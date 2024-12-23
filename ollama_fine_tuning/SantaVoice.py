import ChatTTS
import torch
import torchaudio
import os
import sounddevice as sd

from chatTTS.ChatTTS.tools.logger import get_logger
from chatTTS.ChatTTS.tools.normalizer import normalizer_en_nemo_text, normalizer_zh_tn
from IPython.display import Audio
from chatTTS.ChatTTS.tools.audio import load_audio
file_path = "santa-claus-a-reading-christmas-story-17777.mp3"
info = torchaudio.info(file_path)
print(f"Sample rate: {info.sample_rate}")
sample_rate=info.sample_rate
chat = ChatTTS.Chat()
chat.unload()
chat.load(compile=False)  # 如果需要更好的性能，可以将compile设置为True
spk_smp = chat.sample_audio_speaker(load_audio("./output_segments/santa-claus-a-reading-christmas-story-17777_part1.mp3", 24000))
# spk_smp = chat.sample_audio_speaker(load_audio("santa-claus-a-reading-christmas-story-17777.mp3", 24000))
# spk_smp = chat.sample_audio_speaker(load_audio("../santa-claus-merry-christmas-ho-ho-ho-103426.mp3", sample_rate))
# print(spk_smp)  # save it in order to load the speaker without sample audio next time

print(spk_smp)  # save it in order to load the speaker without sample audio next time
pth_filename = f'./voice_pth/Santa.pth'
torch.save(spk_smp, pth_filename)
params_infer_code = ChatTTS.Chat.InferCodeParams(
    spk_smp=spk_smp,
    txt_smp="与sample.mp3内容完全一致的文本转写。",
    temperature=0.000003,
    top_P=0.7,
    top_K=20
)

wav = chat.infer(
    "四川美食确实以辣闻名，但也有不辣的选择。比如甜水面、赖汤圆、蛋烘糕、叶儿粑等，这些小吃口味温和，甜而不腻，也很受欢迎。",
    params_infer_code=params_infer_code,
)


for w in wav:
    wav_tensor = torch.from_numpy(wav).unsqueeze(0)
    sd.play(wav_tensor.numpy().squeeze(), samplerate=24000)  # 播放生成的音频
    sd.wait()  # 等待播放结束
