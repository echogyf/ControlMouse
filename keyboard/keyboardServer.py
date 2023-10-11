import socket
import msgpack

from pynput import keyboard

# 创建与被控端的UDP套接字
def create_udp_socket(ip, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return udp_socket


# 发送键盘按压事件
def on_press(key):
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


def capture_and_send_keyboard_events(udp_socket, remote_ip, remote_port):
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# 主函数
if __name__ == "__main__":
    remote_ip = '192.168.56.134' # 虚拟机
    # remote_ip = '172.31.110.236' # 本机
    # remote_ip = '172.31.110.64' # 笔记本
    remote_port = 12345  # 与被控端相同的端口

    # 创建UDP套接字
    udp_socket = create_udp_socket(remote_ip, remote_port)
    try:
        # 使用多线程或异步编程来运行鼠标事件捕获函数，以使操作不间断
        import threading

        keyboard_thread = threading.Thread(target=capture_and_send_keyboard_events, args=(udp_socket, remote_ip, remote_port))
        keyboard_thread.start()
        keyboard_thread.join()
    except KeyboardInterrupt:
        print("连接已断开。")
    finally:
        # 不需要关闭UDP套接字
        pass
