import socket
import msgpack
import ctypes
import threading

from pynput import mouse

# 创建与被控端的UDP套接字
def create_udp_socket(ip, port):
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
        # 在发生异常时也要确保event_get_screen被设置，以便程序能继续执行
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

def capture_and_send_click_mouse_events(udp_socket, remote_ip, remote_port):
    event_get_screen.wait()  # 等待event_get_screen，确保getScreen已经执行
    with mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll) as listener:
        listener.join()

# 主函数
if __name__ == "__main__":
    remote_ip = '192.168.56.134' # 虚拟机
    # remote_ip = '172.31.110.236' # 本机
    # remote_ip = '172.31.110.64' # 笔记本
    remote_port = 12345  # 与被控端相同的端口

    event_get_screen = threading.Event()
    event_capture_mouse = threading.Event()

    # 创建UDP套接字
    udp_socket = create_udp_socket(remote_ip, remote_port)

    try:
        # 使用多线程或异步编程来运行鼠标事件捕获函数，以使操作不间断
        import threading

        get_screen_thread = threading.Thread(target=getScreen)
        get_screen_thread.start()
        mouse_click_thread = threading.Thread(target=capture_and_send_click_mouse_events, args=(udp_socket, remote_ip, remote_port))
        mouse_click_thread.start()
        get_screen_thread.join()
        mouse_click_thread.join()
    except KeyboardInterrupt:
        print("连接已断开。")
    finally:
        # 不需要关闭UDP套接字
        pass