import socket
import time
# 设置服务器地址和端口
HOST = '127.0.0.1'  # 本地地址
PORT = 12345        # 监听端口

# 创建 TCP socket 服务器
def run_server():
    # 创建一个 TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # 绑定地址和端口
        server_socket.bind((HOST, PORT))

        # 开始监听客户端连接
        server_socket.listen()
        print(f"Server is listening on {HOST}:{PORT}...")

        while True:
            try:
                # 接收客户端连接
                conn, addr = server_socket.accept()
                print(f"Connected by {addr}")

                # 使用连接处理数据
                with conn:
                    while True:
                        # 接收数据
                        data = conn.recv(1024)
                        if not data:
                            break
                        elif data==b"gift":
                            print(f"Received: {data.decode('utf-8')}")
                            try:
                                conn.sendall(b'start')  # 发送数据给客户端
                                print(f"Sent back:start")
                            except Exception as e:
                                print(f"Error sending data: {e}")
                                break
                            time.sleep(2)
                            conn.sendall("ready".encode('utf-8'))
                            print("Sent: ready")

                            # 持续等待客户端消息，直到接收到"yes"
                            # 等待客户端返回“yes”
                            while(True):
                                data = conn.recv(1024)
                                if data == b"yes":
                                    print("Received: yes. Breaking out of loop.")
                                    conn.sendall("end".encode('utf-8'))
                                    print("Send 'end'")
                                    break
                                else:
                                    break
                        elif data == b"greet" or data == b"circle":
                            data=b'start'

                            conn.sendall(data)

                            print(f"Sent: {data.decode('utf-8')}")
                        elif data == b"story":
                            print(f"Received: {data.decode('utf-8')}")
                            time.sleep(2)
                            data=b'start'
                            conn.sendall(data)
                            while True:
                                data = conn.recv(1024)
                                if data == b"story_end":
                                    print("end process")
                                    break
                                else:
                                    continue
                        else:
                            print(f"Received: {data.decode('utf-8')}")
                            continue

            except Exception as e:
                print(f"Error in connection: {e}")



# 启动服务器
if __name__ == "__main__":
    run_server()
