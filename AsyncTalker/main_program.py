import os
import json
import asyncio
#import numpy as np
#import socket
import zhconv
from audio_recorder import record_audio
from audio_transcriber import transcribe_and_save_audio
from ollama_chat import chat_with_ollama, clear_messages, load_messages,clear_task_items
from audio_tts_handler import text_to_speech  # 导入 TTS 功能
from commandExcute import execute_command
HOST = '127.0.0.1'  # 服务器地址
PORT = 6666  # 服务器端口
def main():
    print("Step 0: 清空消息和任务文件...")
    clear_messages()
    clear_task_items()  # 程序开始时清空历史任务

    while True:
        print("Step 1: 开始录音...")
        record_audio(file_path="audio_input.wav")

        print("Step 2: 转录音频...")
        if os.path.exists("audio_input.wav"):

            transcription_text = transcribe_and_save_audio(file_path="audio_input.wav")
            transcription_text = transcription_text.replace("理由", "礼物")

            print(f"转录结果：{transcription_text}")
            with open("config/transcription.json", "w") as f:
                json.dump({"text": transcription_text}, f)  # Save transcription text as JSON
        else:
            print("音频文件未找到，跳过转录。")
            continue

        print("Step 3: 与 Ollama 模型交互...")
        messages = load_messages()

        response, directive =chat_with_ollama(transcription_text, messages, model="Christmas")
        #response是要转语音的内容，updated_messages是机器人指令
        if response:
            print(f"模型响应：{response}")
            print(f"；指令内容{directive}")
            #directive=zhconv.convert(directive, ZhConvDirection.TRADITIONAL_TO_SIMPLIFIED)
            # Step 4: 调用 TTS 发声
            print("Step 4: 将响应内容转换为语音并播放...")
            text_to_speech(response)
            execute_command(directive)

        else:
            print("未获取到模型响应。")

        # 提示是否继续
        # user_input = input("是否继续？输入 'n' 退出，其他任意键继续：")
        # if user_input.strip().lower() == 'n':
        #     print("程序结束。")
        #     break


if __name__ == "__main__":
    asyncio.run(main())
