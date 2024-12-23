import ollama

# 定义微调的参数
training_data_path = "./Modelfile"  # 替换为您的数据路径

# 微调模型
ollama.finetune(
    model='llama3.2',  # 使用基础模型
    data_file=training_data_path,  # 输入微调数据文件路径
    output_model='custom-llama-robot',  # 输出微调模型的名称
    epochs=3,  # 训练的轮数
    batch_size=4  # 每批次的数据量
)
