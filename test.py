from pynput import mouse

# 鼠标move监听
def on_move(x, y):
    print(f'X: {x}  Y: {y}')


# 鼠标click监听
def on_click(x, y, button, pressed):
    print(f'X: {x}  Y: {y}')
    print(f'鼠标点击键： {button}')
    print(f'鼠标点击状态: {"Pressed" if pressed else "Release"}')

# 鼠标滚轮scroll监听
def on_scroll(x, y, dx, dy):
    print(f'鼠标位置： ({x}, {y})')
    print(f'滚轮参数： ({dx}, {dy})')


with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
    listener.join()

