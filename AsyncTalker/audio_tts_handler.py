import time

import torch
import ChatTTS
import sounddevice as sd
import torch
import soundfile as sf
import cn2an
import socket
from concurrent.futures import ThreadPoolExecutor

PORT = 6666
# 初始化 ChatTTS
chat = ChatTTS.Chat()
chat.load(compile=False)  # 设置为 True 以获得更好的性能
spk = torch.load('../ollama_fine_tuning/voice_pth/girl_37.pth')  # 配置语音生成的参数   8
params_infer_code = ChatTTS.Chat.InferCodeParams(
    spk_emb=spk,
    temperature=0.000003,
    top_P=0.7,
    top_K=20
)
params_refine_text = ChatTTS.Chat.RefineTextParams(
    prompt='[oral_2][laugh_0][break_6]'
)

# 定义线程池
executor = ThreadPoolExecutor(max_workers=1)


def text_to_speech(response_text):
    def generate_and_play_audio(text):
        """使用 ChatTTS 将文本转换为语音并播放"""
        text += "。"  # 确保句子有结尾标点
        text = cn2an.transform(text, "an2cn")
        try:
            wavs = chat.infer([text], skip_refine_text=True, params_refine_text=params_refine_text,
                              params_infer_code=params_infer_code)
            for wav in wavs:
                wav_tensor = torch.from_numpy(wav).unsqueeze(0)
                sd.play(wav_tensor.numpy().squeeze(), samplerate=24000)  # 播放生成的音频
                sd.wait()  # 等待播放结束
        except Exception as e:
            print(f"语音生成或播放失败：{e}")

    try:
        # 创建一个 TCP socket 客户端
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # 尝试连接到 127.0.0.1 和端口 12345
            client_socket.connect(('127.0.0.1', PORT))
            time.sleep(0.1)
            client_socket.sendall(b'talk')
            generate_and_play_audio(response_text)
            time.sleep(1)
            client_socket.sendall(b'talk_end')
    except ConnectionRefusedError:
        # 如果连接失败，捕获异常并输出连接失败
        print("连接失败.")
        generate_and_play_audio(response_text)


def async_text_to_speech(response_text):
    """异步调用 TTS，避免阻塞主线程"""
    executor.submit(text_to_speech, response_text)


if __name__ == "__main__":
    text_to_speech("祝大家圣诞快乐")
