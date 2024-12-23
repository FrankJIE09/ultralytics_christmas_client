import asyncio  # 导入 asyncio 库，用于实现异步 I/O 操作
import argparse  # 导入 argparse 库，用于命令行参数解析

import ollama  # 导入 ollama 库，用于与 Ollama 异步客户端交互


# 定义主函数 main()，包含主要的交互逻辑
async def main():
    parser = argparse.ArgumentParser()  # 创建命令行参数解析器
    # 添加一个 --speak 标志参数，表示是否启用语音功能
    parser.add_argument('--speak', default=False, action='store_true')
    args = parser.parse_args()  # 解析命令行参数

    client = ollama.AsyncClient()  # 创建 Ollama 异步客户端实例

    messages = []  # 初始化消息列表，用于存储用户和助手的消息

    # 进入无限循环，持续接收用户输入和处理对话
    while True:
        if content_in := input('>>> '):  # 获取用户输入
            if content_in.strip().lower() in ["确认", "确认需求"]:
                print("收到，小飒这就行动！！")
                messages = []  # 清空消息列表
                continue  # 跳过当前循环，等待新的输入
            messages.append({'role': 'user', 'content': content_in})  # 将用户消息添加到消息列表中

            content_out = ''  # 初始化输出内容字符串
            message = {'role': 'assistant', 'content': ''}  # 初始化助手消息字典
            # 异步与 Ollama 模型进行聊天，逐步处理响应
            async for response in await client.chat(model='medical', messages=messages, stream=True):
                if response['done']:  # 检查响应是否完成
                    messages.append(message)  # 将完整的助手消息添加到消息列表中

                content = response['message']['content']  # 获取助手消息内容
                print(content, end='', flush=True)  # 打印助手消息内容，不换行，保持流式输出效果

                content_out += content  # 追加内容到输出字符串

                message['content'] += content  # 将助手消息内容追加到当前消息字典

            print()  # 换行输出


# 捕获键盘中断和文件结束错误，退出主函数
try:
    asyncio.run(main())  # 运行异步主函数
except (KeyboardInterrupt, EOFError):
    ...
