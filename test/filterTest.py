import pynput
from pynput import mouse


# 512: 鼠标移动
# 513: 鼠标左键按下
# 514: 鼠标左键抬起
# 515:
# 516: 鼠标右键按下
# 517: 鼠标右键抬起
# 518:
# 519: 鼠标中键按下
# 520: 鼠标中键抬起
# 521:
# 522: 鼠标上下滚轮滚动
# 523: 鼠标侧键按下
# 524: 鼠标侧键抬起
# 525:
# 526: 鼠标左右滚轮滚动
# 527:

# 微软提供 MSLLHOOKSTRUCT api
def win32_event_filter(msg, data):
    if msg == 512:  # 不抑制enter
        print(f'{data.pt.x} , {data.pt.y}')
    elif msg == 513:
        print(f'鼠标左键按下并拦截')
        lis.suppress_event()
    elif msg == 514:
        print(f'鼠标左键抬起并拦截')
        lis.suppress_event()
    elif msg == 516:
        print(f'鼠标右键按下并拦截')
        lis.suppress_event()
    elif msg == 517:
        print(f'鼠标右键抬起并拦截')
        lis.suppress_event()
    elif msg == 519:
        print(f'鼠标中键按下并拦截')
        lis.suppress_event()
    elif msg == 520:
        print(f'鼠标中键抬起并拦截')
        lis.suppress_event()
    elif msg == 522:
        print(f'鼠标上下滚轮拦截 {data.mouseData}')
        if data.mouseData == 4287102976:
            print(f'滚轮向下')
        elif data.mouseData == 7864320:
            print(f'滚轮向上')
        lis.suppress_event()
    elif msg == 526:
        print(f'鼠标左右滚轮拦截 {data.mouseData}')
        lis.suppress_event()
    else:  # 其他一律拦截
        lis.suppress_event()


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


with mouse.Listener(win32_event_filter=win32_event_filter) as lis:
    lis.join()
