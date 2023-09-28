import socket
import msgpack
import time

import pyautogui
import mouse

# 创建与主控端的UDP套接字
def create_udp_socket(ip, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((ip, port))
    print(f"等待连接到 {ip}:{port}...")
    return udp_socket

# 接收和处理事件
def receive_and_process_events(udp_socket):
    event_counter = 0
    start_time = time.time()

    try:
        while True:
            data, _ = udp_socket.recvfrom(1024)  # 接收数据包

            unpacker = msgpack.Unpacker(raw=False)
            unpacker.feed(data)

            for event_data in unpacker:
                event = event_data  # 不需要再次解包，因为数据已经解包过

                if event['type'] == 'mouse':
                    count = event['data']['count']
                    x, y = event['data']['x'], event['data']['y']
                    print('count:' + str(count).rjust(2) + '  X:' + str(x).rjust(2) + '  Y:' + str(y).rjust(2))
                    pyautogui.moveTo(x, y, duration=0.1)

                elif event['type'] == 'click':
                    button = event['button']
                    x, y = event['x'], event['y']
                    print(f'Received {button} click at X:{x} Y:{y}')
                    if button == 'left':
                        pyautogui.click(x, y, button='left')
                    elif button == 'right':
                        pyautogui.click(x, y, button='right')

                event_counter += 1

                if event_counter % 100 == 0:
                    elapsed_time = time.time() - start_time
                    receive_rate = event_counter / elapsed_time
                    print(f"接收速率: {receive_rate:.2f} events/second")

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