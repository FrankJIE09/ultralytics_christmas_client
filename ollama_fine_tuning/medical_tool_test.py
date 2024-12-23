import json
import asyncio
import ollama
# 模拟一个API调用，获取物品的抓取指令
def get_item_pickup(item: str, quantity: int) -> str:
    items = {"试管", "注射器", "输液袋", "手套", "口罩"}
    if item in items:
        return json.dumps({'task': f'抓取{quantity}个{item}'})
    else:
        return json.dumps({'error': f'物品 {item} 未找到'})

async def run(model: str):
    # 初始化会话与用户请求
    client = ollama.AsyncClient()  # 正确初始化客户端
    messages = [{'role': 'user', 'content': '我需要一个试管,两个手套，三个输液袋，一个耳机'}]

    # 第一次API调用：发送用户请求和函数描述给模型
    response = await client.chat(
        model=model,
        messages=messages,
        tools=[
            {
                'type': 'function',
                'function': {
                    'name': 'get_item_pickup',
                    'description': '获取物品抓取指令',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'item': {
                                'type': 'string',
                                'description': '需要抓取的物品名称',
                            },
                            'quantity': {
                                'type': 'integer',
                                'description': '抓取的数量',
                            },
                        },
                        'required': ['item', 'quantity'],
                    },
                },
            },
        ],
    )

    # 将模型的响应加入对话历史
    messages.append(response['message'])

    # 检查模型是否决定使用提供的函数
    if not response['message'].get('tool_calls'):
        print("模型未使用函数。模型的回复是：")
        print(response['message']['content'])
        return

    # 处理模型调用的函数
    if response['message'].get('tool_calls'):
        available_functions = {
            'get_item_pickup': get_item_pickup,
        }
        for tool in response['message']['tool_calls']:
            function_to_call = available_functions[tool['function']['name']]
            function_response = function_to_call(tool['function']['arguments']['item'], tool['function']['arguments']['quantity'])
            # 将函数响应加入对话中
            messages.append(
                {
                    'role': 'tool',
                    'content': function_response,
                }
            )

    # 第二次API调用：获取模型的最终回复
    final_response = await client.chat(model=model, messages=messages)
    print(final_response['message']['content'])

# 运行异步函数
asyncio.run(run('medical'))
