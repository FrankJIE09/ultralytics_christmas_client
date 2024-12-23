# 定义不同功能的函数
import os
import json
import asyncio
import socket
import random
import sounddevice as sd
import torch
import soundfile as sf

from inspect import iscoroutinefunction
from audio_recorder import record_audio
from audio_transcriber import transcribe_and_save_audio
from ollama_chat import chat_with_ollama, clear_messages, load_messages, clear_task_items
from audio_tts_handler import text_to_speech

# 定义不同功能的函数
HOST = '127.0.0.1'  # 服务器地址
PORT = 6666  # 服务器端口

christmas_greetings = [
    "愿这美好的节日充满欢声笑语，愿圣诞的钟声带来无尽的幸福与好运，祝你和家人平安、喜乐、团圆！",
    "圣诞快乐！愿你在这特别的日子里感受到无尽的爱与温暖，幸福常伴！",
    "圣诞到，祝愿你生活甜如蜜，心情美如画，愿所有的心想事成都成为现实，愿所有的幸福都与你常伴！",
    "雪花飞舞，点亮浪漫的夜晚；铃声轻响，传递温馨的祝愿。愿你的圣诞如诗如梦，生活幸福美满！",
    "圣诞老人说，你今年表现很棒，礼物箱都塞不下啦！提前祝你圣诞快乐，开心每一天！",
    "在这闪烁的圣诞灯光下，愿你感受到未来的希望和力量。新的一年，愿你勇敢追梦，收获属于自己的幸福与成功！",
    "圣诞节是团圆的季节，愿家人间的欢声笑语充满每一个角落，愿爱和祝福围绕在你左右，圣诞快乐！",
    "May the joy and peace of Christmas be with you throughout the year. Wishing you a season filled with love and laughter!",
    "祝你圣诞奇妙！！！",
    "愿圣诞的钟声带来平安与希望，愿节日的欢乐充满你的心扉，圣诞快乐！",
    "在这个充满爱与温暖的季节，愿你拥抱幸福，拥有美好的每一天！",
    "愿圣诞的奇迹在你身边发生，生活如童话般美好！",
    "圣诞老人已经在路上了，希望他不会把你的礼物忘在北极！",
    "今天是吃喝不胖的特别日子，尽情享受吧，圣诞快乐！",
    "圣诞的快乐就像圣诞树上的星星，永远点亮你的每一天！",
    "新的一年即将到来，愿你在节日中感受到希望的力量，迈向更美好的未来！",
    "圣诞节不仅是团聚的时刻，更是一个新的起点，愿你每一天都充满热情与期待！",
    "愿圣诞带来的喜悦点燃你的心，愿你的梦想在新的一年绽放！",
    "圣诞节最幸福的事，就是和最爱的人围坐在一起，共享节日的喜悦与温暖！"

]
gift_prompts = [
    "准备好迎接惊喜了吗？",
    "圣诞老人要来送礼物啦，你准备好了吗？",
    "是不是已经迫不及待要打开礼物了？",
    "准备好接收节日的惊喜了吗？",
    "礼物时刻到了，做好准备了吗？",
    "圣诞魔法正在降临，你准备好迎接了吗？",
    "现在是接受祝福与礼物的时间，你准备好了吗？"
]
delivery_prompts = [
    "叮叮叮，圣诞礼物已送到，请查收！",
    "礼物已到达你的身边，快看看是什么吧！",
    "圣诞钟声响起，礼物已经悄悄送达！",
    "你的礼物到了，快打开看看吧！",
    "节日的惊喜已经到达，满满的祝福送给你！",
    "礼物送达！愿它带给你无尽的欢乐！",
    "叮叮叮，礼物已准时到达，请笑纳！"
]
retry_prompts = [
    "哎呀，有点小失误，请稍等，我再试一次！",
    "出了一点小问题，不要着急，我马上再来一次！",
    "别慌，我这就重新处理一下，很快就好！",
    "稍等一下哦，我需要再试一次！",
    "不好意思，出现了点小插曲，让我再来试试！",
    "抱歉出了一点问题，小朋友不要急，我马上解决！",
    "哎呀，好像哪里没对，再给我一点时间试一次！"
]
def handle_gift(giftColor):
    result = ""
    selected_prompt = random.choice(gift_prompts)
    selected_delivery_prompt = random.choice(delivery_prompts)
    selected_retry_prompt = random.choice(retry_prompts)
    try:
        # 创建一个 TCP socket 客户端
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # 尝试连接到 127.0.0.1
            client_socket.connect(('127.0.0.1', PORT))
            max_attempts = 5  # 设置最大失败次数
            failed_attempts = 0  # 初始化失败次数

            client_socket.sendall(b'gift')
            while True:

                    response1 = client_socket.recv(1024)
                    if response1 == b'ready':
                        print(f"Received response: {response1.decode('utf-8')}")
                        text_to_speech(selected_prompt)
                        #print("Step 0: 清空消息和任务文件...")
                        #clear_messages()
                        #clear_task_items()  # 程序开始时清空历史任务
                        while True:
                            print("Step 1: 开始录音...")
                            record_audio(file_path="audio_ready.wav")

                            print("Step 2: 转录音频...")
                            if os.path.exists("audio_ready.wav"):
                                transcription_text = transcribe_and_save_audio(file_path="audio_ready.wav")
                                print(f"转录结果：{transcription_text}")
                                with open("config/transcription.json", "w") as f:
                                    json.dump({"text": transcription_text}, f)  # Save transcription text as JSON
                            else:
                                print("音频文件未找到，跳过转录。")

                            print("Step 3: 与 Ollama 模型交互...")
                            messages = load_messages()
                            response2, directive = chat_with_ollama(transcription_text, messages, model="Translator")
                            # response2, directive = chat_with_ollama(transcription_text, messages,model="Translator")
                            # response是要转语音的内容，updated_messages是机器人指令
                            if response2:
                                print(f"模型响应：{response2}")
                                if response2 == "yes":
                                    client_socket.sendall(b'yes')
                                    response3 = client_socket.recv(1024)
                                    if not response3:
                                        print("No response")
                                    if response3 == b'end':
                                        print("received end")
                                        text_to_speech(selected_delivery_prompt)
                                        result = "任务完成！"
                                        return result
                                    else:
                                        print(f"received {response3}")
                                        break
                                elif response2 == "nogift":
                                    client_socket.sendall(b'no_gift')
                                    text_to_speech(selected_retry_prompt)
                                    break
                            else:
                                print("未获取到模型响应。")

                    else:
                        print("RobotError")
                        result = "RobotError"


    except ConnectionRefusedError:
        print("连接失败")
        # 如果连接失败，捕获异常并输出连接失败
        return "连接失败"
    return result


def tell_story():
    # 设置服务器地址和端口

    try:
        # 连接服务器
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            conn.connect((HOST, PORT))  # 连接服务器
            print(f"Connected to {HOST}:{PORT}")

            # 检查 ./story 文件夹是否存在
            story_folder = './story'
            if not os.path.exists(story_folder) or not os.path.isdir(story_folder):
                print("错误: 没有找到故事文件夹.")
                return

            # 获取文件夹中的所有 txt 文件
            wav_files = [f for f in os.listdir(story_folder) if f.endswith('.wav')]

            # 如果没有 txt 文件，返回错误
            if not wav_files:
                print("错误: 没有找到故事文件.")
                return

            # 向服务器发送 "story" 请求
            conn.sendall(b"story")
            print("Sent: story")
            response0 = conn.recv(1024)
            if not response0:
                print("No response")
            else:
                print(f"Received response: {response0.decode('utf-8')}")
                if response0.startswith(b'start'):
                    # 随机选择一个 txt 文件
                    random_story_file = random.choice(wav_files)
                    file_path = os.path.join(story_folder, random_story_file)
                    try:
                        # 读取 .wav 文件
                        wav, samplerate = sf.read(file_path)  # `wav` 是音频数据，`samplerate` 是采样率

                        # 转换为 torch tensor 并添加批次维度
                        wav_tensor = torch.from_numpy(wav).unsqueeze(0)

                        # 播放音频
                        sd.play(wav_tensor.numpy().squeeze(), samplerate=samplerate)  # 播放生成的音频
                        sd.wait()  # 等待播放结束
                        print("播放完成.")

                    except Exception as e:
                        print(f"播放音频时出错: {e}")
            # 向服务器发送 "end" 请求
            conn.sendall(b"story_end")
            print("Sent: end")

    except socket.error:
        # 如果无法连接到服务器
        print("未能连接到服务器")

    except Exception as e:
        # 处理其他异常
        print(f"发生错误: {e}")


def greet():
    selected_greeting = random.choice(christmas_greetings)
    try:
        # 创建一个 TCP socket 客户端
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # 尝试连接到 127.0.0.1 和端口 12345
            client_socket.connect(('127.0.0.1', PORT))

            # 发送字符串 '1'
            client_socket.sendall(b'greet')

            # 如果需要接收返回消息，可以调用 recv()
            response = client_socket.recv(1024)

            if response:
                print("Received:", response.decode('utf-8'))
                if response.startswith(b'ready'):
                    text_to_speech(selected_greeting)
            else:
                print("No response received from the server.")
            response1 = client_socket.recv(1024)
            if response1.startswith(b'end'):
                return "任务完成"
            else:
                print("no end response")
        return "任务完成"

    except ConnectionRefusedError:
        print("连接失败")
        # 如果连接失败，捕获异常并输出连接失败
        return "连接失败"


def draw_circle():
    selected_circle = random.choice(christmas_greetings)
    try:
        # 创建一个 TCP socket 客户端
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # 尝试连接到 127.0.0.1 和端口 12345
            client_socket.connect(('127.0.0.1', PORT))

            # 发送字符串 '1'
            client_socket.sendall(b'circle')

            # 如果需要接收返回消息，可以调用 recv()
            response = client_socket.recv(1024)

            if response:
                print("Received:", response.decode('utf-8'))
                if response.startswith(b'ready'):
                    text_to_speech(selected_circle)
            else:
                print("No response received from the server.")
            response1 = client_socket.recv(1024)
            if response1.startswith(b'end'):
                return "任务完成"
            else:
                print("no end response")
        return "任务完成"

    except ConnectionRefusedError:
        print("连接失败")
        # 如果连接失败，捕获异常并输出连接失败
        return "连接失败"


def thanks():
    try:
        # 创建一个 TCP socket 客户端
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # 尝试连接到 127.0.0.1 和端口 12345
            client_socket.connect(('127.0.0.1', PORT))

            # 发送字符串 '1'
            client_socket.sendall(b'thanks')

        return "任务完成"

    except ConnectionRefusedError:
        # 如果连接失败，捕获异常并输出连接失败
        print("连接失败.")
        return "连接失败"


# 主函数：根据接收到的字符串的第一部分选择相应的操作
def execute_command(command: str) -> str:
    # 将命令按空格分成两部分
    command_parts = command.split(",", 1)  # 只分割一次

    # 定义指令映射字典
    command_map = {
        "礼物": lambda: handle_gift('gift'),  # 使用 lambda 函数传递参数
        "故事": tell_story,
        #"打招呼": greet,
        "画圈": draw_circle,
        "感谢": thanks
    }

    # 获取命令的第一部分
    command_key = command_parts[0]
    command_func = command_map.get(command_key, lambda: "Unrecognized command.")
    result = command_func()

    # 直接返回结果
    return result


# 测试用例（如果直接运行此脚本，会调用下面的部分）
if __name__ == "__main__":
    # 示例测试
    test_commands = [

        "打招呼,1"
    ]

    for command in test_commands:
        print(f"Input command: {command} -> Output: {execute_command(command)}")
