import socket
import threading

# 定义接收数据的线程
def receive_data(client_socket):
    while True:
        try:
            # 接收来自服务器的数据
            data = client_socket.recv(1024)  # 1024字节缓冲区
            if not data:
                print("Disconnected from server")
                break
            print(f"Received from server: {data.decode()}")
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# 定义发送数据的功能
def send_data(client_socket):
    while True:
        try:
            message = input("Enter message to send to server: ")
            if message.lower() == 'exit':
                print("Exiting...")
                break
            # 发送数据给服务器
            client_socket.send(message.encode())
        except Exception as e:
            print(f"Error sending data: {e}")
            break

def main():
    # 创建一个 TCP socket 客户端
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # 尝试连接到服务器（此处为本地服务器地址和端口号）
        client_socket.connect(('127.0.0.1', 12345))

        print("Connected to server.")

        # 创建一个线程用于接收数据
        receive_thread = threading.Thread(target=receive_data, args=(client_socket,))
        receive_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        receive_thread.start()

        # 创建一个线程用于发送数据
        send_thread = threading.Thread(target=send_data, args=(client_socket,))
        send_thread.daemon = True
        send_thread.start()

        # 等待发送线程和接收线程完成
        send_thread.join()
        receive_thread.join()

if __name__ == '__main__':
    main()
