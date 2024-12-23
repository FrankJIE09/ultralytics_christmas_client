import os
import torch
import ChatTTS
import cn2an
import soundfile as sf

# 初始化 ChatTTS
chat = ChatTTS.Chat()
chat.load(compile=False)  # 加载 ChatTTS 模型
spk = torch.load('../ollama_fine_tuning/voice_pth/girl_37.pth')  # 语音生成参数
params_infer_code = ChatTTS.Chat.InferCodeParams(
    spk_emb=spk,
    temperature=0.000003,
    top_P=0.7,
    top_K=20
)
params_refine_text = ChatTTS.Chat.RefineTextParams(
    prompt='[oral_2][laugh_0][break_6]'
)

# 定义文本转语音函数
def text_to_speech(text, output_path):
    try:
        refined_text = cn2an.transform(text, "an2cn")  # 转换阿拉伯数字为中文数字
        wavs = chat.infer([refined_text], skip_refine_text=True,
                          params_refine_text=params_refine_text,
                          params_infer_code=params_infer_code)
        for wav in wavs:
            wav_tensor = torch.from_numpy(wav)
            sf.write(output_path, wav_tensor.numpy().squeeze(), samplerate=24000)  # 保存为 WAV 文件
        print(f"生成音频成功：{output_path}")
    except Exception as e:
        print(f"音频生成失败：{e}")

# 遍历 ./story 文件夹中的 .txt 文件
def process_story_files():
    story_dir = './story'
    if not os.path.exists(story_dir):
        print(f"文件夹 {story_dir} 不存在")
        return

    for file_name in os.listdir(story_dir):
        if file_name.endswith('.txt'):
            txt_path = os.path.join(story_dir, file_name)
            wav_path = os.path.splitext(txt_path)[0] + '.wav'

            # 如果 WAV 文件已经存在，跳过
            if os.path.exists(wav_path):
                print(f"音频文件已存在，跳过：{wav_path}")
                continue

            # 读取文本内容并生成音频
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                if text:  # 确保文件非空
                    print(f"处理文本文件：{txt_path}")
                    text_to_speech(text, wav_path)
                else:
                    print(f"文本文件为空，跳过：{txt_path}")
            except Exception as e:
                print(f"无法处理文件 {txt_path}：{e}")

# 执行脚本
if __name__ == '__main__':
    process_story_files()
