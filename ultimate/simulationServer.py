import socket
import msgpack
import time

from pynput import mouse
import pyautogui

# 创建与被控端的UDP套接字
def create_udp_socket(ip, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return udp_socket

# 发送鼠标移动事件
def send_mouse_event(udp_socket, event_data, remote_ip, remote_port):
    event = {
        'type': 'mouse',
        'data': event_data
    }
    event_msgpack = msgpack.packb(event, use_bin_type=True)
    udp_socket.sendto(event_msgpack, (remote_ip, remote_port))

# 发送鼠标点击事件
def on_click(x, y, button, pressed):
    event_type = "Pressed" if pressed else "Release"
    print(f"点击右键" if button == "Button.right" else "点击左键")
    event = {
        'type': event_type,
        'x': x,
        'y': y,
        'button': str(button)
    }
    event_msgpack = msgpack.packb(event, use_bin_type=True)
    udp_socket.sendto(event_msgpack, (remote_ip, remote_port))

# 捕获并发送鼠标事件
def capture_and_send_mouse_events(udp_socket, remote_ip, remote_port):
    event_counter = 0
    start_time = time.time()
    last_display_time = start_time
    display_interval = 1.0  # 显示速率的时间间隔

    while True:
        x, y = pyautogui.position()
        send_mouse_event(udp_socket, {'count': event_counter,'x': x, 'y': y}, remote_ip, remote_port)
        print('count:' + str(event_counter).rjust(2) + '  X:' + str(x).rjust(2) + '  Y:' + str(y).rjust(2))
        event_counter += 1

        current_time = time.time()
        elapsed_time = current_time - start_time

        if current_time - last_display_time >= display_interval:
            send_rate = event_counter / elapsed_time
            print(f"发送速率: {send_rate:.2f} events/second")
            last_display_time = current_time

        time.sleep(0.1)  # 控制事件发送频率（单位：秒）

def capture_and_send_click_mouse_events(udp_socket, remote_ip, remote_port):
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

# 主函数
if __name__ == "__main__":
    # remote_ip = '192.168.56.134'
    remote_ip = '172.31.110.236'
    # remote_ip = '172.31.110.64'
    remote_port = 12345  # 与被控端相同的端口

    # 创建UDP套接字
    udp_socket = create_udp_socket(remote_ip, remote_port)

    try:
        # 使用多线程或异步编程来运行鼠标事件捕获函数，以使操作不间断
        import threading

        mouse_move_thread = threading.Thread(target=capture_and_send_mouse_events, args=(udp_socket, remote_ip, remote_port))
        mouse_click_thread = threading.Thread(target=capture_and_send_click_mouse_events, args=(udp_socket, remote_ip, remote_port))
        mouse_move_thread.start()
        mouse_click_thread.start()
        mouse_move_thread.join()
        mouse_click_thread.join()
    except KeyboardInterrupt:
        print("连接已断开。")
    finally:
        # 不需要关闭UDP套接字
        pass
