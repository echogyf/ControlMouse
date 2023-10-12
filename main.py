import socket
import sys
import time

import msgpack
import ctypes
import threading

from pynput import mouse
from pynput import keyboard
from pynput.keyboard import Key


# #######################################################主控端代码#######################################################
# 创建与被控端的UDP套接字
def create_mian_udp_socket(ip, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return udp_socket


# 发送主控端显示分辨率
def getScreen():
    try:
        # 获取当前屏幕分辨率
        user32 = ctypes.windll.user32
        width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        event = {
            'type': 'Screen',
            'width': width,
            'height': height,
        }
        event_msgpack = msgpack.packb(event, use_bin_type=True)
        udp_socket.sendto(event_msgpack, (remote_ip, remote_port))
        event_get_screen.set()  # 设置event_get_screen，表示已经获取屏幕分辨率
    except Exception as e:
        print(f"发生异常：{e}")
        event_get_screen.set()


# 发送鼠标移动事件
def on_move(x, y):
    event = {
        'type': 'Move',
        'x': x,
        'y': y,
    }
    print(f'X: {x}  Y: {y}')
    event_msgpack = msgpack.packb(event, use_bin_type=True)
    udp_socket.sendto(event_msgpack, (remote_ip, remote_port))


# 发送鼠标点击事件
def on_click(x, y, button, pressed):
    event_type = "Pressed" if pressed else "Release"
    if event_type == "Pressed":
        print(f"按下右键" if button == "Button.right" else "按下左键")
    elif event_type == "Release":
        print(f"松开右键" if button == "Button.right" else "松开左键")
    event = {
        'type': event_type,
        'x': x,
        'y': y,
        'button': str(button)
    }
    event_msgpack = msgpack.packb(event, use_bin_type=True)
    udp_socket.sendto(event_msgpack, (remote_ip, remote_port))


# 发送鼠标滚轮事件
def on_scroll(x, y, dx, dy):
    event = {
        'type': 'Scroll',
        'x': x,
        'y': y,
        'dx': dx,
        'dy': dy
    }
    if dy < 0:
        print(f'鼠标滚轮向下滚动 {dy}')
    elif dy > 0:
        print(f'鼠标滚轮向上滚动 {dy}')
    elif dx < 0:
        print(f'鼠标滚轮向右滚动 {dx}')
    elif dx > 0:
        print(f'鼠标滚轮向左滚动 {dx}')
    event_msgpack = msgpack.packb(event, use_bin_type=True)
    udp_socket.sendto(event_msgpack, (remote_ip, remote_port))


# 发送键盘按压事件
def on_press(key):
    global exit_program
    if key == Key.esc:
        event = {
            'type': 'Exit'
        }
        event_msgpack = msgpack.packb(event, use_bin_type=True)
        udp_socket.sendto(event_msgpack, (remote_ip, remote_port))
        exit_program = True
    else:
        try:
            key_char = key.char  # 获取按键的字符表示形式
            key_type = 'char'
        except AttributeError:
            key_char = str(key)  # 如果按键没有字符表示形式，将其转换为字符串
            key_type = 'special'

        event = {
            'type': 'Keyboard',
            'statue': 'pressed',
            'keyType': key_type,
            'key': key_char
        }
        print('{0} 按下'.format(key_char))
        event_msgpack = msgpack.packb(event, use_bin_type=True)
        udp_socket.sendto(event_msgpack, (remote_ip, remote_port))


# 发送键盘松开事件
def on_release(key):
    try:
        key_char = key.char  # 获取按键的字符表示形式
        key_type = 'char'
    except AttributeError:
        key_char = str(key)  # 如果按键没有字符表示形式，将其转换为字符串
        key_type = 'special'

    event = {
        'type': 'Keyboard',
        'statue': 'released',
        'keyType': key_type,
        'key': key_char
    }
    print('{0} 松开'.format(key_char))
    event_msgpack = msgpack.packb(event, use_bin_type=True)
    udp_socket.sendto(event_msgpack, (remote_ip, remote_port))


# ----------------------------------------------------------------------------------------------------------------------
# 被控端代码
# 创建与主控端的UDP套接字
def create_controlled_udp_socket(ip, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((ip, port))
    print(f"等待连接到 {ip}:{port}...")
    return udp_socket


# 接收和处理事件
def receive_and_process_events(udp_socket):
    global host_height, host_width
    # 获取当前屏幕分辨率
    user32 = ctypes.windll.user32
    controlled_width, controlled_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    print(f'当前分辨率{controlled_width}，{controlled_height}')
    try:
        while True:
            data, _ = udp_socket.recvfrom(1024)  # 接收数据包
            unpacker = msgpack.Unpacker(raw=False)
            unpacker.feed(data)

            control1 = mouse.Controller()  # 获取鼠标操控对象
            control2 = keyboard.Controller()  # 获取键盘操控对象

            for event_data in unpacker:
                event = event_data

                if event['type'] == 'Exit':
                    print("程序退出")
                    time.sleep(1)
                    sys.exit(0)
                if event['type'] == 'Screen':
                    host_width, host_height = event['width'], event['height']
                    print(f'主控端分辨率{host_width}，{host_height}')
                elif event['type'] == 'Move':
                    x, y = event['x'] * int(controlled_width) / int(host_width), event['y'] * int(
                        controlled_height) / int(host_height)
                    control1.position = (x, y)
                    print(f'X: {x:.0f}  Y: {y:.0f}')

                elif event['type'] == "Pressed":
                    button = event['button']
                    if button == 'Button.left':
                        control1.press(mouse.Button.left)
                        print(f"按下鼠标左键")
                    elif button == 'Button.right':
                        control1.press(mouse.Button.right)
                        print(f"按下鼠标右键")

                elif event['type'] == "Release":
                    button = event['button']
                    if button == 'Button.left':
                        control1.release(mouse.Button.left)
                        print(f"松开鼠标左键")
                    elif button == 'Button.right':
                        control1.release(mouse.Button.right)
                        print(f"松开鼠标右键")

                elif event['type'] == "Scroll":
                    dx, dy = event['dx'], event['dy']
                    if dy < 0:
                        control1.scroll(0, dy)
                        print(f'鼠标滚轮向下滚动 {dy}')
                    elif dy > 0:
                        control1.scroll(0, dy)
                        print(f'鼠标滚轮向上滚动 {dy}')
                    elif dx < 0:
                        control1.scroll(dx, 0)
                        print(f'鼠标滚轮向右滚动 {dx}')
                    elif dx > 0:
                        control1.scroll(dx, 0)
                        print(f'鼠标滚轮向左滚动 {dx}')

                elif event['type'] == 'Keyboard':
                    if event['statue'] == 'pressed':
                        key = event['key']
                        if key in special_keys:
                            key = special_keys[key]
                        control2.press(key)
                        print(f'按下 {key}')

                    elif event['statue'] == 'released':
                        key = event['key']
                        if key in special_keys:
                            key = special_keys[key]
                        control2.release(key)
                        print(f'松开 {key}')
    except KeyboardInterrupt:
        print("连接已断开.")
    finally:
        # 不需要关闭UDP套接字
        pass


special_keys = {
    'Key.shift': Key.shift,
    'Key.shift_l': Key.shift_l,
    'Key.shift_r': Key.shift_r,
    'Key.esc': Key.esc,
    'Key.space': Key.space,
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
    'Key.ctrl': Key.ctrl,
    'Key.ctrl_l': Key.ctrl_l,
    'Key.ctrl_r': Key.ctrl_r,
    'Key.tab': Key.tab,
    'Key.caps_lock': Key.caps_lock,
    'Key.cmd': Key.cmd,
    'Key.cmd_r': Key.cmd_r,
    'Key.cmd_l': Key.cmd_l,
    'Key.alt': Key.alt,
    'Key.alt_l': Key.alt_l,
    'Key.alt_r': Key.alt_r,
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
    'Key.print_screen': Key.print_screen,
    'Key.scroll_lock': Key.scroll_lock,
    'Key.num_lock': Key.num_lock,
    'Key.menu': Key.menu
}

# 主函数
if __name__ == "__main__":
    choice = input("输入1为主控端，输入2为被控端:\n")
    if choice == "1":
        exit_program = False
        remote_ip = '192.168.56.134'  # 虚拟机
        # remote_ip = '172.31.110.236' # 本机
        # remote_ip = '172.31.110.64' # 笔记本
        remote_port = 12345  # 与被控端相同的端口

        event_get_screen = threading.Event()
        event_capture_mouse = threading.Event()
        exit_event = threading.Event()

        # 创建UDP套接字
        udp_socket = create_mian_udp_socket(remote_ip, remote_port)
        try:
            # 连接事件以及释放
            getScreen()
            mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll)
            key_listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True)
            # 启动监听线程
            mouse_listener.start()
            key_listener.start()
            print(exit_program)
            while True:
                if exit_program:
                    mouse_listener.stop()
                    key_listener.stop()
                    print("程序退出")
                    time.sleep(1)
                    sys.exit(0)

        except KeyboardInterrupt:
            print("连接已断开。")
        finally:
            # 不需要关闭UDP套接字
            pass
    elif choice == "2":
        local_ip = '0.0.0.0'  # 监听所有可用接口
        local_port = 12345  # 与主控端相同的端口

        # 创建UDP套接字
        udp_socket = create_controlled_udp_socket(local_ip, local_port)

        # 接收和处理事件，实时显示在控制台
        receive_and_process_events(udp_socket)
    else:
        print("选择无效。")
