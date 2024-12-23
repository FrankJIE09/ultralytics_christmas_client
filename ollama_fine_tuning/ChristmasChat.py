import asyncio  # 导入 asyncio 库，用于实现异步 I/O 操作
import argparse  # 导入 argparse 库，用于命令行参数解析

import ollama  # 导入 ollama 库，用于与 Ollama 异步客户端交互


# 定义一些空的函数作为占位符，用于指令调用
def handle_story(story_id):
    print(f"\n执行故事功能，故事ID: {story_id}")

def handle_unknown():
    print("\n未知指令")

# 定义一个函数来处理指令
def handle_directive(directive):
    if directive.startswith('故事'):
        _, story_id = directive.split(',')
        handle_story(story_id)
    else:
        handle_unknown()

# 定义主函数 main()，包含主要的交互逻辑
async def main():
    parser = argparse.ArgumentParser()  # 创建命令行参数解析器
    # 添加一个 --speak 标志参数，表示是否启用语音功能
    parser.add_argument('--speak', default=False, action='store_true')
    args = parser.parse_args()  # 解析命令行参数

    client = ollama.AsyncClient()  # 创建 Ollama 异步客户端实例

    messages = []  # 初始化消息列表，用于存储用户和助手的消息
    directive_buffer = ""
    # 进入无限循环，持续接收用户输入和处理对话
    while True:
        if content_in := input('>>> '):  # 获取用户输入
            messages.append({'role': 'user', 'content': content_in})  # 将用户消息添加到消息列表中

            content_out = ''  # 初始化输出内容字符串
            message = {'role': 'assistant', 'content': ''}  # 初始化助手消息字典
            # 异步与 Ollama 模型进行聊天，逐步处理响应
            async for response in await client.chat(model='Christmas', messages=messages, stream=True):
                content = response['message']['content']  # 获取助手消息内容

                # 如果指令缓存中已有未完成的指令，拼接内容
                if directive_buffer or '<' in content:
                    directive_buffer += content  # 累积内容
                    if '>' in directive_buffer:  # 检查是否有完整指令
                        text, remaining = directive_buffer.split('<', 1)
                        directive= remaining
                        print(text, end='', flush=True)  # 打印内容（不包括指令部分）
                        if not response['done']:
                            continue
                else:
                    print(content, end='', flush=True)



                    message['content'] += content  # 完整内容记录
                    content_out += content

                if response['done']:
                    # 确保所有内容已处理完毕
                    if directive_buffer:
                        if '>' in directive_buffer:  # 如果缓存中有完整指令
                            _, directive = directive_buffer.split('<', 1)
                            directive = directive.strip('>')
                            handle_directive(directive)  # 根据指令内容调用对应函数
                            directive_buffer = ""  # 清空缓存
                        else:
                            print(f"\n警告：未完成的指令内容被丢弃: {directive_buffer}")
                            directive_buffer = ""
                # 等到响应完成后处理指令

            messages.append(message)  # 将完整的助手消息添加到消息列表中

            print()  # 换行输出


# 捕获键盘中断和文件结束错误，退出主函数
try:
    asyncio.run(main())  # 运行异步主函数
except (KeyboardInterrupt, EOFError):
    ...
