import datetime
import math
import os
import random
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

# グローバル変数
mouse_xy = pyautogui.position()
dx = 100
interval_time = 10
is_running = True

history_max = 25
mouse_history = deque([True] * history_max, maxlen=history_max)


def euclidean_distance(point1, point2):
    squared_diff_sum = sum((p2 - p1) ** 2 for p1, p2 in zip(point1, point2))
    return math.sqrt(squared_diff_sum)


def is_used_mouse():
    global mouse_xy

    if not is_running:
        return False

    mouse_xy_current = pyautogui.position()
    distance = euclidean_distance(mouse_xy, mouse_xy_current)
    mouse_xy = mouse_xy_current

    res = distance > abs(dx)
    mouse_history.append(res)
    is_not_used = all(not x for x in mouse_history)

    # mouse_historyの内容を表示
    print(f"マウス履歴: {list(mouse_history)}, 使用中: {not is_not_used}")

    return not is_not_used


def is_stop_time():
    current_hour = datetime.datetime.now().hour
    return current_hour == 21


def mouse_move():
    global dx, is_running
    check_time_interval = 600  # 10分ごとに時刻をチェック
    last_time_check = time.time()

    while True:
        current_time = time.time()

        if current_time - last_time_check >= check_time_interval:
            last_time_check = current_time
            if is_stop_time() and is_running:
                is_running = False

        # 停止中は何もしない
        if not is_running:
            time.sleep(1)
            continue

        # マウス履歴をチェックして動いていたら何もしない
        if is_used_mouse():
            time.sleep(interval_time)
            continue

        # より激しい動きを実装
        try:
            # ランダムな方向に移動
            direction = pyautogui.position()
            rand_x = dx if random.random() > 0.5 else -dx
            rand_y = dx // 2 if random.random() > 0.5 else -dx // 2

            pyautogui.move(rand_x, rand_y)
            time.sleep(0.5)  # 短い待機
            pyautogui.move(-rand_x, -rand_y)  # 元の位置に戻す
        except:
            pyautogui.move(-dx, 0)

        dx = -dx if random.random() > 0.7 else dx  # 70%の確率で方向転換
        time.sleep(interval_time)


def check_finishkey(key):
    if key == keyboard.Key.esc:
        return False


def setup(icon):
    icon.visible = True


def on_start(icon, item):
    global is_running, mouse_history
    is_running = True

    # mouse_historyをすべてTrueにリセット
    mouse_history.clear()
    for _ in range(history_max):
        mouse_history.append(True)

    print("マウス自動移動を開始しました")
    print(f"現在のマウス履歴: {list(mouse_history)}")


def on_stop(icon, item):
    global is_running
    is_running = False
    print("マウス自動移動を停止しました")
    print(f"現在のマウス履歴: {list(mouse_history)}")


def on_quit(icon, item):
    global is_running
    is_running = False
    icon.stop()
    key_listener.stop()


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Startボタンの有効/無効を制御する関数
def is_start_enabled(item):
    return not is_running


# Stopボタンの有効/無効を制御する関数
def is_stop_enabled(item):
    return is_running


def create_tray_icon():
    icon_image = Image.open(resource_path("assets/leaf.ico"))
    menu = Menu(
        MenuItem("Start", on_start, enabled=is_start_enabled),
        MenuItem("Stop", on_stop, enabled=is_stop_enabled),
        MenuItem("Quit", on_quit),
    )
    icon = Icon("leaf_icon", icon_image, menu=menu)
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
