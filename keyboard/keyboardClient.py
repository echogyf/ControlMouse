import socket
import msgpack

from pynput import keyboard
from pynput.keyboard import Key

special_keys = {
    'Key.shift': Key.shift,
    'Key.shift_r': Key.shift_r,
    'Key.esc': Key.esc,
    'Key.f1': Key.f1,
    'Key.f2': Key.f2,
    'Key.f3': Key.f3,
    'Key.f4': Key.f4,
    'Key.f5': Key.f5,
    'Key.f6': Key.f6,
    'Key.f7': Key.f7,
    'Key.f8': Key.f8,
    'Key.f9': Key.f9,
    'Key.f10': Key.f10,
    'Key.f11': Key.f11,
    'Key.f12': Key.f12,
    'Key.delete': Key.delete,
    'Key.ctrl_l': Key.ctrl_l,
    'Key.ctrl_r': Key.ctrl_r,
    'Key.tab': Key.tab,
    'Key.caps_lock': Key.caps_lock,
    'Key.cmd': Key.cmd,
    'Key.alt_l': Key.alt_l,
    'Key.alt_gr': Key.alt_gr,
    'Key.up': Key.up,
    'Key.down': Key.down,
    'Key.left': Key.left,
    'Key.right': Key.right,
    'Key.enter': Key.enter,
    'Key.backspace': Key.backspace,
    'Key.home': Key.home,
    'Key.end': Key.end,
    'Key.page_up': Key.page_up,
    'Key.page_down': Key.page_down,
    'Key.pause': Key.pause,
    'Key.insert': Key.insert,
    'Key.print_screen': Key.print_screen
}

# 创建与主控端的UDP套接字
def create_udp_socket(ip, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((ip, port))
    print(f"等待连接到 {ip}:{port}...")
    return udp_socket


# 接收和处理事件
def receive_and_process_events(udp_socket):
    try:
        while True:
            data, _ = udp_socket.recvfrom(1024)  # 接收数据包
            unpacker = msgpack.Unpacker(raw=False)
            unpacker.feed(data)

            control = keyboard.Controller()  # 获取键盘操控对象

            for event_data in unpacker:
                event = event_data

                if event['type'] == 'Keyboard':
                    if event['statue'] == 'pressed':
                        key = event['key']
                        if key in special_keys:
                            key = special_keys[key]
                        control.press(key)
                        print(f'按下 {key}')

                    elif event['statue'] == 'released':
                        key = event['key']
                        if key in special_keys:
                            key = special_keys[key]
                        control.release(key)
                        print(f'松开 {key}')

    except KeyboardInterrupt:
        print("连接已断开.")
    finally:
        # 不需要关闭UDP套接字
        pass


# 主函数
if __name__ == "__main__":
    local_ip = '0.0.0.0'  # 监听所有可用接口
    local_port = 12345  # 与主控端相同的端口

    # 创建UDP套接字
    udp_socket = create_udp_socket(local_ip, local_port)

    # 接收和处理事件，实时显示在控制台
    receive_and_process_events(udp_socket)
