from transformers import AutoModelForSpeechSeq2Seq

model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-tiny")
help(model.generate)  # 查看模型的生成方法支持的参数
