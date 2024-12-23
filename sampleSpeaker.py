import ChatTTS
import torch
import torchaudio
import os

from chatTTS.ChatTTS.tools.logger import get_logger
from chatTTS.ChatTTS.tools.normalizer import normalizer_en_nemo_text, normalizer_zh_tn
from IPython.display import Audio
from chatTTS.ChatTTS.tools.audio import load_audio

chat = ChatTTS.Chat()
chat.load(compile=False)  # 如果需要更好的性能，可以将compile设置为True

spk_smp = chat.sample_audio_speaker(load_audio("./santa-claus-merry-christmas-ho-ho-ho-103426.mp3", 24000))
print(spk_smp)  # save it in order to load the speaker without sample audio next time

params_infer_code = ChatTTS.Chat.InferCodeParams(
    spk_smp=spk_smp,
    txt_smp="与sample.mp3内容完全一致的文本转写。",
)

wav = chat.infer(
    "四川美食确实以辣闻名，但也有不辣的选择。比如甜水面、赖汤圆、蛋烘糕、叶儿粑等，这些小吃口味温和，甜而不腻，也很受欢迎。",
    params_infer_code=params_infer_code,
)