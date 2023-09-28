from pynput import mouse
import socket
import msgpack

# 被控端的IP地址和端口
remote_ip = '192.168.56.134'
remote_port = 12345

# 创建UDP套接字
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 鼠标move监听
def on_move(x, y):
    event = {
        'type': 'mouse_move',
        'x': x,
        'y': y
    }
    event_msgpack = msgpack.packb(event, use_bin_type=True)
    udp_socket.sendto(event_msgpack, (remote_ip, remote_port))

# 鼠标click监听
def on_click(x, y, button, pressed):
    event_type = 'mouse_click' if pressed else 'mouse_release'
    event = {
        'type': event_type,
        'x': x,
        'y': y,
        'button': str(button)
    }
    event_msgpack = msgpack.packb(event, use_bin_type=True)
    udp_socket.sendto(event_msgpack, (remote_ip, remote_port))

# 启动鼠标监听
with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
    listener.join()