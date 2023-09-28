import socket
import json
import pyautogui  # 用于模拟鼠标和键盘输入


# 建立与计算机B的TCP连接
def establish_connection(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    return client_socket


# 捕获鼠标和键盘事件，然后发送它们
def capture_and_send_events(client_socket):
    while True:
        # 捕获鼠标事件或键盘事件，这里以键盘事件为例
        key = input("请输入一个键：")

        # 构建事件数据包
        event = {
            'type': 'keyboard',
            'key': key
        }

        # 将事件编码为JSON字符串
        event_json = json.dumps(event)

        # 发送事件数据包
        client_socket.send(event_json.encode())


# 主函数
if __name__ == "__main__":
    remote_ip = '计算机B的IP地址'
    remote_port = 12345  # 选择一个未被占用的端口

    # 建立连接
    connection = establish_connection(remote_ip, remote_port)

    # 开始捕获和发送事件
    capture_and_send_events(connection)