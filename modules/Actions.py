import time
import ctypes
import pygetwindow as gw
from typing import Optional

SendInput = ctypes.windll.user32.SendInput

# Constants for commonly used keys
W = 0x11
A = 0x1E
S = 0x1F
D = 0x20

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class Actions:
    def __init__(self, window_title_substring: Optional[str] = None):
        self.window_title_substring = window_title_substring

    @staticmethod
    def is_window_focused(title_substring):
        try:
            active_window = gw.getActiveWindow()
            return title_substring.lower() in active_window.title.lower()
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def press_key(self, hex_key_code):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hex_key_code, 0x0008, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_key(self, hex_key_code):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hex_key_code, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def move_forward(self):
        self.press_key(W)
        time.sleep(0.5)
        self.release_key(W)

    def move_back(self):
        self.press_key(S)
        time.sleep(0.5)
        self.release_key(S)

    def turn_left(self):
        self.press_key(A)
        time.sleep(0.5)
        self.release_key(A)

    def turn_right(self):
        self.press_key(D)
        time.sleep(0.5)
        self.release_key(D)

    def move_mouse_left(self):
        ctypes.windll.user32.mouse_event(0x0001, -50, 0, 0, 0)  # x, y, dwData, dwExtraInfo
        time.sleep(0.1)

    def move_mouse_right(self):
        ctypes.windll.user32.mouse_event(0x0001, 50, 0, 0, 0)
        time.sleep(0.1)

if __name__ == "__main__":
    actions = Actions(window_title_substring="NeosVR")
    while True:
        if actions.is_window_focused(actions.window_title_substring):
            print("Neos is focused")
            actions.move_forward()
            time.sleep(1)
            actions.move_back()
            time.sleep(1)
            actions.turn_left()
            time.sleep(1)
            actions.turn_right()
            time.sleep(1)
            actions.move_mouse_left()
            time.sleep(1)
            actions.move_mouse_right()
        time.sleep(1)
