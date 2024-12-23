import asyncio
import numpy as np
import ollama
import os
import json

from sympy.calculus.util import continuous_domain

from config_handler import load_config, get_target_points
import re

MESSAGES_FILE = "config/messages.npy"
CONFIG_FILE = "./config/config.yaml"
TASK_FILE = "config/task.json"

# 设置默认的任务数量系数
TASK_COEFFICIENT = 1  # 系数可根据需求调整


def load_messages():
    if os.path.exists(MESSAGES_FILE):
        return np.load(MESSAGES_FILE, allow_pickle=True).tolist()
    return []


def save_messages(messages):
    np.save(MESSAGES_FILE, np.array(messages, dtype=object))


def clear_messages():
    """清除 messages.npy 文件中的数据"""
    if os.path.exists(MESSAGES_FILE):
        np.save(MESSAGES_FILE, np.array([], dtype=object))
        print(f"{MESSAGES_FILE} 文件已清空。")
    else:
        print(f"{MESSAGES_FILE} 文件不存在，无需清空。")


def load_task_items():
    """加载已保存的任务清单"""
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    return {}


def save_task_items(task_items):
    """保存任务清单到文件"""
    with open(TASK_FILE, "w") as f:
        json.dump(task_items, f, ensure_ascii=False)


def clear_task_items():
    """清除任务清单文件"""
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "w") as f:
            json.dump({}, f, ensure_ascii=False)
        print(f"{TASK_FILE} 文件已清空。")
    else:
        print(f"{TASK_FILE} 文件不存在，无需清空。")


def parse_task_response(response_text):
    """
    从 LLaMA 返回的任务指令中解析任务清单，并添加系数。
    示例输入：
    任务指令：抓取 2 个试管、2 个口罩。
    输出：{"试管": 2, "口罩": 2}
    """
    # 定义物品关键字列表
    items_list = ["试管", "注射器", "输液袋", "手套", "口罩"]
    items = {}

    # 遍历关键字列表并检查是否在任务指令中
    for item in items_list:
        if item in response_text:
            # 提取对应物品的数量
            pattern = rf"(\d+)\s*个?\s*{item}"  # 匹配数量 + 单位（如“个”）+ 物品名称
            match = re.search(pattern, response_text)
            if match:
                quantity = int(match.group(1))
                items[item] = quantity * TASK_COEFFICIENT

    return items



# async def chat_with_ollama(user_input, messages, model="medical"):
#     client = ollama.AsyncClient()
#
#     # 如果是确认指令，直接执行保存的任务清单
#     #如果是有记忆的用这一句
#     #messages.append({'role': 'user', 'content': user_input})
#     # 清空旧的消息，仅存储当前输入
#     messages = [{'role': 'user', 'content': user_input}]
#     response_text = ""
#     assistant_message = {'role': 'assistant', 'content': ''}
#     directive_buffer = ""  # 缓存指令内容
#     directive=""
#     async for response in await client.chat(model=model, messages=messages, stream=True):
#         content = response['message']['content']
#         directive_buffer += content
#         if response['done']:
#             assistant_message['content']=directive_buffer
#             if '<' in directive_buffer:
#                 response_text, directive = directive_buffer.split('<', 1)  # 分成两部分
#                 response_text = response_text.strip()  # 去除前后空格
#                 print(response_text)
#                 # 检查 message 是否以 '>' 结尾
#                 if directive.endswith('>'):
#                     directive = directive.strip('>')  # 去掉结尾的 '>'
#
#                 else:
#                     directive = 'unknown'  # 如果没有 '>'，将 message 设置
#             else:
#                 response_text = directive_buffer
#                 directive = 'unknown'
#         # 清空缓冲区，准备下一次指令
#         else:
#             continue
#     directive_buffer = ""
#     print()
#     #messages.append(assistant_message)
#     #save_messages(messages)
#     return response_text, directive

def chat_with_ollama(user_input, messages, model="medical"):
    import ollama
    import asyncio

    client = ollama.Client()  # 使用同步客户端

    # 如果是确认指令，直接执行保存的任务清单
    # 如果是有记忆的用这一句
    # messages.append({'role': 'user', 'content': user_input})
    # 清空旧的消息，仅存储当前输入
    messages = [{'role': 'user', 'content': user_input}]
    response_text = ""
    assistant_message = {'role': 'assistant', 'content': ''}
    directive_buffer = ""  # 缓存指令内容
    directive = ""

    response = client.chat(model=model, messages=messages, stream=True)

    for chunk in response:  # 使用同步 for 循环
        content = chunk['message']['content']
        directive_buffer += content
        if chunk['done']:
            assistant_message['content'] = directive_buffer
            if '<' in directive_buffer:
                response_text, directive = directive_buffer.split('<', 1)  # 分成两部分
                response_text = response_text.strip()  # 去除前后空格
                print(response_text)
                # 检查 directive 是否以 '>' 结尾
                if directive.endswith('>'):
                    directive = directive.strip('>')  # 去掉结尾的 '>'
                else:
                    directive = 'unknown'  # 如果没有 '>'，将 directive 设置为 'unknown'
            else:
                response_text = directive_buffer
                directive = 'unknown'
        else:
            continue

    directive_buffer = ""
    print()
    # messages.append(assistant_message)
    # save_messages(messages)
    return response_text, directive


async def execute_task(task_items):
    debug = True
    if not debug:
        from robot_controller import RobotController

        """
        执行机器人任务，根据任务清单驱动机器人移动。
        """
        # 加载配置文件
        config = load_config(CONFIG_FILE)
        robot_params = config.get("robot_connection", {})
        target_points = config.get("target_points", {})

        # 初始化机器人
        controller = RobotController(robot_type="CPS", connection_params=robot_params)

        # 执行任务逻辑
        for item, quantity in task_items.items():
            if item not in target_points:
                print(f"未找到 {item} 的目标点位，请检查配置文件。")
                continue

            target_pose = target_points[item]
            print(f"开始处理 {item}，需要移动 {quantity} 次。")
            for i in range(quantity):
                print(f"第 {i + 1} 次移动到 {item} 的目标点位：{target_pose}")
                # 上方移动
                controller.move_robot(
                    [target_pose[0], target_pose[1], target_pose[2] + 100, target_pose[3], target_pose[4], target_pose[5]])
                # 到目标点
                controller.move_robot(target_pose)
                # 回到上方
                controller.move_robot(
                    [target_pose[0], target_pose[1], target_pose[2] + 100, target_pose[3], target_pose[4], target_pose[5]])

        controller.disconnect()
        print("所有任务完成。")
    return "机器人已完成移动任务。"


if __name__ == "__main__":
    async def main():
        """
        主函数：清空消息文件并运行主流程。
        """
        clear_messages()
        clear_task_items()  # 程序开始时清空历史任务
        print("历史消息和任务文件已清除，开始运行主程序。")
        messages = load_messages()

        # 模拟用户输入
        print("请输入指令：")
        while True:
            user_input = input(">>> ").strip()
            if user_input.lower() == "exit":
                print("程序结束。")
                break

            # 调用聊天逻辑
            # response, updated_messages = await chat_with_ollama(user_input, messages, model="medical")
            response, updated_messages =chat_with_ollama(user_input, messages, model="medical")
            print(f"\n响应：{response}")
            messages = updated_messages


    # 运行异步主函数
    asyncio.run(main())
