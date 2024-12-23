# testAudio.py

from AsyncTalker.audio_tts_handler import text_to_speech

def test_text_to_speech():
    response_text = "Hello, this is a test message."
    try:
        text_to_speech(response_text)  # 调用 text_to_speech 函数
        print("语音转换成功")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    test_text_to_speech()
