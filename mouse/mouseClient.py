import socket
import msgpack
import ctypes

from pynput import mouse


# 创建与主控端的UDP套接字
def create_udp_socket(ip, port):
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

            control = mouse.Controller()  # 获取鼠标操控对象

            for event_data in unpacker:
                event = event_data

                if event['type'] == 'Screen':
                    host_width, host_height = event['width'], event['height']
                    print(f'主控端分辨率{host_width}，{host_height}')
                elif event['type'] == 'Move':
                    x, y = event['x'], event['y']
                    control.position = (x * int(controlled_width) / int(host_width), y * int(controlled_height) / int(host_height))
                    print(f'X: {x}  Y: {y}')

                elif event['type'] == "Pressed":
                    button = event['button']
                    if button == 'Button.left':
                        control.press(mouse.Button.left)
                        print(f"按下鼠标左键")
                    elif button == 'Button.right':
                        control.press(mouse.Button.right)
                        print(f"按下鼠标右键")

                elif event['type'] == "Release":
                    button = event['button']
                    if button == 'Button.left':
                        control.release(mouse.Button.left)
                        print(f"松开鼠标左键")
                    elif button == 'Button.right':
                        control.release(mouse.Button.right)
                        print(f"松开鼠标右键")

                elif event['type'] == "Scroll":
                    dx, dy = event['dx'], event['dy']
                    if dy < 0:
                        control.scroll(0, dy)
                        print(f'鼠标滚轮向下滚动 {dy}')
                    elif dy > 0:
                        control.scroll(0, dy)
                        print(f'鼠标滚轮向上滚动 {dy}')
                    elif dx < 0:
                        control.scroll(dx, 0)
                        print(f'鼠标滚轮向右滚动 {dx}')
                    elif dx > 0:
                        control.scroll(dx, 0)
                        print(f'鼠标滚轮向左滚动 {dx}')
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
