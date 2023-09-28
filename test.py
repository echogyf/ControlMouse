from pynput import mouse

# 鼠标move监听
def on_move(x, y):
    print(f'X: {x}  Y: {y}')


# 鼠标click监听
def on_click(x, y, button, pressed):
    print(f'X: {x}  Y: {y}')
    print(f'Click button： {button}')
    print(f'Click state: {"Pressed" if pressed else "Release"}')




with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
    listener.join()

