import socket
import msgpack
import pyautogui

# 被控端的IP地址和端口
local_ip = '0.0.0.0'
local_port = 12345

# 创建UDP套接字
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((local_ip, local_port))

while True:
    data, _ = udp_socket.recvfrom(1024)  # 接收数据包

    event = msgpack.unpackb(data, raw=False)

    if event['type'] == 'mouse_move':
        x, y = event['x'], event['y']
        pyautogui.moveTo(x, y, duration=0.1)
    elif event['type'] == 'mouse_click':
        x, y, button = event['x'], event['y'], event['button']
        if button == 'Button.left':
            pyautogui.click(x, y, button='left')
        elif button == 'Button.right':
            pyautogui.click(x, y, button='right')