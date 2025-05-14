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
from pynput import keyboard, mouse
from pystray import Icon, Menu, MenuItem

# マウス座標が画面左上に行ったときに終了する機能を無効にする
pyautogui.FAILSAFE = False

mouse_xy = pyautogui.position()
dx = 100
max_distance = math.ceil(dx * math.sqrt(5 / 4))
interval_time = 1
is_running = True

history_max = 250
controll_history = deque([True] * history_max, maxlen=history_max)


def euclidean_distance(point1, point2):
    squared_diff_sum = sum((p2 - p1) ** 2 for p1, p2 in zip(point1, point2))
    return math.sqrt(squared_diff_sum)


def is_used_mouse():
    global mouse_xy
    mouse_xy_current = pyautogui.position()
    distance = euclidean_distance(mouse_xy, mouse_xy_current)
    mouse_xy = mouse_xy_current

    res = distance > max_distance

    controll_history.append(res)
    is_not_used = all(not x for x in controll_history)

    # print(
    #     f"操作履歴: {list(controll_history)}, 距離: {distance:.1f} px, 使用中: {not is_not_used}"
    # )

    if not is_running:
        return False

    return not is_not_used


def is_stop_time():
    current_hour = datetime.datetime.now().hour
    return current_hour == 21


def mouse_move():
    global dx, is_running
    check_time_interval = 600
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

        # 操作履歴をチェックして動いていたら何もしない
        if is_used_mouse():
            time.sleep(interval_time)
            continue

        try:
            rand_x = dx if random.random() > 0.5 else -dx
            rand_y = dx // 2 if random.random() > 0.5 else -dx // 2

            pyautogui.move(rand_x, rand_y)
            time.sleep(0.5)  # 短い待機
        except:
            pyautogui.move(-dx, 0)

        dx = -dx if random.random() > 0.7 else dx
        time.sleep(interval_time)


def check_key(key):
    global controll_history
    is_continue = True
    if key == keyboard.Key.esc:
        is_continue = False
        # ESCキーが押されたときにマウスリスナーも停止する
        mouse_listener.stop()
    else:
        controll_history.append(True)
    return is_continue


def setup(icon):
    icon.visible = True


def on_start(icon, item):
    global is_running, controll_history
    is_running = True

    # historyをすべてTrueにリセット
    controll_history.clear()
    for _ in range(history_max):
        controll_history.append(True)

    print("メソッドを開始しました")


def on_stop(icon, item):
    global is_running
    is_running = False
    print("メソッドを停止しました")


def on_quit(icon, item):
    global is_running
    is_running = False
    icon.stop()
    key_listener.stop()
    mouse_listener.stop()


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


def on_click(x, y, button, pressed):
    global controll_history
    if pressed:  # クリック時（押した時）にのみTrue追加
        controll_history.append(True)
    return True  # Listenerを継続


def on_scroll(x, y, dx, dy):
    global controll_history
    controll_history.append(True)
    return True  # Listenerを継続


# キーボードリスナーとマウスリスナーを作成
key_listener = keyboard.Listener(on_press=check_key)
mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)

# 両方のリスナーを開始
key_listener.start()
mouse_listener.start()

# 両方のリスナーが終了するまで待機
key_listener.join()
mouse_listener.join()

sys.exit()
