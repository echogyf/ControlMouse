from pynput import keyboard

def on_press(key):
    print(type(key))
    print(type(key.char))
    print('{0} 按下'.format(key))


def on_release(key):
    print('{0} 松开'.format(key))
    if key == keyboard.Key.esc:
        return False

# Collect events until released
with keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
    listener.join()