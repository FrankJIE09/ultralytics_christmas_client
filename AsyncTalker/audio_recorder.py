import pyaudio
import numpy as np
import wave
import time


# 录音函数
def record_audio(file_path="audio_input.wav"):
    # 配置参数
    FORMAT = pyaudio.paInt16  # 音频格式为16位
    CHANNELS = 1  # 单声道
    RATE = 16000  # 采样率为16000 Hz
    CHUNK = 1024  # 每次读取的音频数据块大小
    PRE_RECORD_DURATION = 1  # 预录音时长1秒
    START_THRESHOLD = 50  # 启动录音的音量阈值
    STOP_THRESHOLD = 70  # 停止录音的音量阈值
    MIN_SILENCE_DURATION = 1  # 停止录音的静音持续时间（秒）
    MAX_DURATION = 5    # 创建PyAudio实例
    audio = pyaudio.PyAudio()

    # 计算预录音的数据块数
    pre_record_chunks = int(PRE_RECORD_DURATION * RATE / CHUNK)

    # 录音缓冲区
    recorded_data = []

    # 打开音频流
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("等待音量超过启动阈值以开始录音...")

    # 预录音，捕获启动前的1秒音频
    for _ in range(pre_record_chunks):
        data = stream.read(CHUNK)
        recorded_data.append(data)

    print(f"预录音数据已捕获，准备开始正式录音。")

    silence_counter = 0  # 用于检测连续静音的时长
    recording_started = False  # 录音是否已开始
    start_time = None
    try:
        while True:
            # 读取当前音频数据块
            data = stream.read(CHUNK)
            recorded_data.append(data)

            # 将音频数据转换为numpy数组
            audio_data = np.frombuffer(data, dtype=np.int16)

            # 计算当前音频块的音量（计算RMS）
            volume = np.sqrt(np.mean(audio_data ** 2))

            print(f"当前音量: {volume:.2f}")

            # 判断音量是否超过启动阈值开始录音
            if not recording_started and volume > START_THRESHOLD:
                recording_started = True
                recorded_data = recorded_data[-10:] if len(recorded_data) >= 10 else recorded_data
                start_time = time.time()
                print("音量超过启动阈值，开始正式录音。")

            # 如果已开始录音，判断是否满足结束条件
            if recording_started:
                if time.time()-start_time > MAX_DURATION:
                    print(f"录制时长: {time.time()-start_time}")
                    break
                if volume < STOP_THRESHOLD:
                    silence_counter += 1  # 记录静音时长（每次音量低于结束阈值）
                    print(f"音量低于结束阈值，静音计数器: {silence_counter}")

                    if silence_counter >= MIN_SILENCE_DURATION * RATE / CHUNK:  # 静音超过 1 秒
                        print("音量持续低于结束阈值，停止录音，并再录音 1 秒。")
                        # 延迟录音 1 秒
                        for _ in range(int(RATE / CHUNK)):
                            data = stream.read(CHUNK)
                            recorded_data.append(data)
                        break  # 结束录音
                else:
                    silence_counter = 0  # 如果音量恢复，重置静音计数器

    finally:
        # 结束录音，关闭流
        print("停止录音，正在保存文件...")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # 保存音频数据到文件
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(recorded_data))

        print(f"录音保存到 {file_path}")

if __name__ == '__main__':

# 调用录音函数
    record_audio("audio_input.wav")
