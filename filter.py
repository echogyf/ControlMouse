import socket

import win32con
import win32console
import win32gui
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


def win32_event_filter(msg, data):
    if msg in mouse_mapping:
        event_type, button = mouse_mapping[msg]
        event = {
            'type': event_type,
            'button': button
        }

        if event_type == 'Move':
            event['x'] = data.pt.x
            event['y'] = data.pt.y

        if event_type == 'Scroll' and button == 'column':
            if data.mouseData == 4287102976:
                event['dx'] = 0
                event['dy'] = -1
                # print(f'滚轮向下')
            elif data.mouseData == 7864320:
                event['dx'] = 0
                event['dy'] = 1
                # print(f'滚轮向上')

        if event_type == 'Scroll' and button == 'row':
            if data.mouseData <= 629145600:
                event['dx'] = 1
                event['dy'] = 0
                # print(f'滚轮向左')
            elif data.mouseData >= 3390570496:
                event['dx'] = -1
                event['dy'] = 0
                # print(f'滚轮向右')
        # print(f'X: {data.pt.x}  Y: {data.pt.y}' if event_type == 'Move' else f'鼠标{button} {event_type}')
        # print(event)
        event_msgpack = msgpack.packb(event, use_bin_type=True)
        udp_socket.sendto(event_msgpack, (remote_ip, remote_port))
        if event_type != 'Move':
            mouse_listener.suppress_event()


mouse_mapping = {
    512: ('Move', None),
    513: ('Pressed', 'Button.left'),
    514: ('Release', 'Button.left'),
    516: ('Pressed', 'Button.right'),
    517: ('Release', 'Button.right'),
    519: ('Pressed', 'Button.middle'),
    520: ('Release', 'Button.middle'),
    522: ('Scroll', 'column'),
    526: ('Scroll', 'row'),
}


# 发送键盘按压事件
def on_press(key):
    global exit_program, cmd_press
    if key == Key.esc and cmd_press:
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
        if key == Key.cmd:
            cmd_press = True
        else:
            cmd_press = False
        event = {
            'type': 'Keyboard',
            'statue': 'pressed',
            'keyType': key_type,
            'key': key_char
        }
        # print('{0} 按下'.format(key_char))
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
    # print('{0} 松开'.format(key_char))
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
                    control2.release(Key.cmd)
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
                    elif button == 'Button.middle':
                        control1.press(mouse.Button.middle)
                        print(f"按下鼠标中键")

                elif event['type'] == "Release":
                    button = event['button']
                    if button == 'Button.left':
                        control1.release(mouse.Button.left)
                        print(f"松开鼠标左键")
                    elif button == 'Button.right':
                        control1.release(mouse.Button.right)
                        print(f"松开鼠标右键")
                    elif button == 'Button.middle':
                        control1.release(mouse.Button.middle)
                        print(f"松开鼠标中键")

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


# 特殊按键
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


# 最小化窗口
def minimize_console_window():
    hwnd = win32console.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)


# 将窗口尺寸恢复到最小化之前尺寸
def restore_console_window():
    hwnd = win32console.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


# 主函数
if __name__ == "__main__":
    choice = input("输入1为主控端，输入2为被控端:\n")
    if choice == "1":
        exit_program = False
        cmd_press = False
        remote_ip = '192.168.56.134'  # 虚拟机
        # remote_ip = '172.31.110.236' # 本机
        # remote_ip = '172.31.110.64' # 笔记本
        remote_port = 12345  # 与被控端相同的端口

        event_get_screen = threading.Event()
        event_capture_mouse = threading.Event()
        exit_event = threading.Event()

        # 启动程序并最小化窗口，使用相对路径
        minimize_console_window()
        # 创建UDP套接字
        udp_socket = create_mian_udp_socket(remote_ip, remote_port)
        try:
            # 连接事件以及释放
            getScreen()
            mouse_listener = mouse.Listener(win32_event_filter=win32_event_filter)
            key_listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True)
            # 启动监听线程
            mouse_listener.start()
            key_listener.start()
            # print(exit_program)
            while True:
                if exit_program:
                    mouse_listener.stop()
                    key_listener.stop()
                    restore_console_window()
                    print("程序退出!")
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
