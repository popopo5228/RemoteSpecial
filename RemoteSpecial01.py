import math
import os
import sys
import threading
import time
from collections import deque

import pyautogui
from PIL import Image
from pynput import keyboard
from pystray import Icon, Menu, MenuItem

# マウス座標が画面左上に行ったときに終了する機能を無効にする
pyautogui.FAILSAFE = False

mouse_xy = pyautogui.position()
dx = 10
interval_time = 10

history_max = 25
mouse_history = deque([True] * history_max, maxlen=history_max)


def euclidean_distance(point1, point2):
    squared_diff_sum = sum((p2 - p1) ** 2 for p1, p2 in zip(point1, point2))
    return math.sqrt(squared_diff_sum)


def is_used_mouse():
    global mouse_xy
    mouse_xy_current = pyautogui.position()
    distance = euclidean_distance(mouse_xy, mouse_xy_current)
    mouse_xy = mouse_xy_current

    res = distance > abs(dx)
    mouse_history.append(res)
    is_not_used = all(not x for x in mouse_history)
    return not is_not_used


def mouse_move():
    global dx
    while True:
        # マウス履歴をチェックして動いていたら何もしない
        if is_used_mouse():
            time.sleep(interval_time)
            continue
        try:
            pyautogui.move(dx, 0)
        except:
            pyautogui.move(-dx, 0)
        dx *= -1
        time.sleep(interval_time)


def check_finishkey(key):
    if key == keyboard.Key.esc:
        return False


def setup(icon):
    icon.visible = True


def on_quit(icon, item):
    icon.stop()
    key_listener.stop()


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def create_tray_icon():
    icon_image = Image.open(resource_path("assets/fg.ico"))
    icon = Icon("fg_icon", icon_image, menu=Menu(MenuItem("Quit", on_quit)))
    icon.run(setup=setup)


icon_thread = threading.Thread(target=create_tray_icon)
icon_thread.daemon = True
icon_thread.start()

thread = threading.Thread(target=mouse_move)
thread.daemon = True
thread.start()


with keyboard.Listener(on_press=check_finishkey) as key_listener:
    key_listener.join()

sys.exit()
