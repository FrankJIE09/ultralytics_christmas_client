import whisper
import pyaudio
import numpy as np
import ollama
import ChatTTS  # 引入 ChatTTS
import torch
import soundfile as sf  # Use soundfile for saving audio files
import torchaudio
import sounddevice as sd
import random
import cn2an

seed = 5  # 5  7  9 12
random.seed(seed)
torch.manual_seed(seed)
# 加载 Whisper 模型
whisper_model = whisper.load_model("large")

# 设置音频录制参数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Whisper 需要 16kHz 的采样率
CHUNK = 1024  # 音频块大小
RECORD_SECONDS = 5  # 每次录制时长，可调整

audio = pyaudio.PyAudio()
seed = 5   #5  7  9 12
random.seed(seed)
torch.manual_seed(seed)
# 初始化 ChatTTS
chat = ChatTTS.Chat()
chat.load(compile=False)  # 设置为 True 以获得更好的性能
rand_spk = torch.load('./voice_pth/girl_16.pth')# 配置语音生成的参数
params_infer_code = ChatTTS.Chat.InferCodeParams(
    spk_emb=rand_spk,     # 使用采样的讲话者嵌入
    temperature=0.000003,      # 自定义温度，控制生成的多样性和随机性
    top_P=0.7,            # 使用Top-P采样进行解码
    top_K=20              # 使用Top-K采样进行解码
)
params_refine_text = ChatTTS.Chat.RefineTextParams(
    prompt='[oral_2][laugh_0][break_6]',  # 设定具体的语音提示符
)
def record_audio():
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    print("请说话...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    # 将录制的音频转为 numpy 数组并转换为 Whisper 兼容的浮点格式
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
    return audio_data

def transcribe_audio(audio_data):
    result = whisper_model.transcribe(audio_data, language="zh")
    return result['text']

while True:

    # 获取音频输入并转录为文本
    audio_input = record_audio()
    user_input = transcribe_audio(audio_input)
    print(f"你: {user_input}")

    if user_input.strip().lower() == "再见" or user_input.strip().lower() == "退出":
        print("再见！")
        break

    # 使用 Ollama 和 LLaMA 进行对话
    stream = ollama.chat(
        model='medical',
        messages=[{'role': 'user', 'content': user_input}],
        stream=True,  # 开启流式输出
    )

    response_text = ""
    print("模型: ", end="")
    for chunk in stream:
        # 实时输出模型生成的响应
        response_chunk = chunk['message']['content']
        print(response_chunk, end="", flush=True)
        response_text += response_chunk
    print()  # 换行
    response_text = cn2an.transform(response_text, "an2cn")
    # 使用 ChatTTS 进行语音合成并播放输出文本
    wavs = chat.infer([response_text],skip_refine_text=True, params_refine_text=params_refine_text, params_infer_code=params_infer_code)
    for wav in wavs:

        # 播放生成的音频（可以根据你的播放需求自定义音频处理方式）
        wav_tensor = torch.from_numpy(wav).unsqueeze(0)
        # 用 sounddevice 播放，或者其他音频库播放音频
        sd.play(wav_tensor.numpy().squeeze(), samplerate=24000)
        sd.wait()  # 等待播放结束
