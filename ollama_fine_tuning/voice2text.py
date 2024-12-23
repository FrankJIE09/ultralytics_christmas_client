import whisper
import pyaudio
import numpy as np
import wave
import os
from datetime import datetime
import time

# 加载 Whisper 模型
whisper_model = whisper.load_model("large")

# 设置音频录制参数
FORMAT = pyaudio.paInt16  # 音频格式为 16 位整型
CHANNELS = 1  # 单声道
RATE = 16000  # Whisper 需要 16kHz 的采样率
CHUNK = 1024  # 音频块大小
BASE_DIR = "recorded_audio"  # 存储录音的基础文件夹
THRESHOLD = 500  # 音量阈值，用于控制录音的开始和结束
MAX_SILENCE_DURATION = 3  # 最大允许的静音时长（秒）

audio = pyaudio.PyAudio()

def record_audio():
    # 打开音频流
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    print("请开始说话...")

    frames = []
    recording = False
    silence_start = None  # 记录静音开始的时间

    while True:
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # 检测音量是否超过阈值
        if np.abs(audio_data).mean() > THRESHOLD:
            if not recording:
                print("录音开始...")
            recording = True
            frames.append(data)
            silence_start = None  # 重置静音计时
        elif recording:
            # 如果已经开始录音且音量低于阈值，记录静音开始时间
            if silence_start is None:
                silence_start = time.time()
            else:
                # 检测是否超过最大静音时长
                elapsed_silence = time.time() - silence_start
                if elapsed_silence > MAX_SILENCE_DURATION:
                    print("录音结束。")
                    break

    stream.stop_stream()
    stream.close()

    # 使用当前日期生成文件夹路径
    date_str = datetime.now().strftime("%Y%m%d")
    date_dir = os.path.join(BASE_DIR, date_str)

    # 如果日期文件夹不存在，则创建
    if not os.path.exists(date_dir):
        os.makedirs(date_dir)

    # 使用当前时间生成文件名
    timestamp = datetime.now().strftime("%H%M%S")
    filename = os.path.join(date_dir, f"recording_{timestamp}.wav")
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # 将录制的音频数据转换为 numpy 数组，并转为 Whisper 兼容的浮点格式
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
    return audio_data

def transcribe_audio(audio_data):
    # 使用 Whisper 模型将音频转录为文本
    result = whisper_model.transcribe(audio_data, language="zh")
    return result['text']

while True:
    # 录制音频并将其转为文本
    audio_input = record_audio()
    user_input = transcribe_audio(audio_input)
    print(f"你: {user_input}")

    # 如果用户输入“再见”或“退出”，则结束程序
    if user_input.strip().lower() == "再见" or user_input.strip().lower() == "退出":
        print("再见！")
        break
