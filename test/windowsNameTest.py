import win32con
import win32console
import win32gui


# 获取所有当前打开的窗口的标题
def minimize_console_window():
    hwnd = win32console.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)


# 将窗口尺寸恢复到最小化之前尺寸
def restore_console_window():
    hwnd = win32console.GetConsoleWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
