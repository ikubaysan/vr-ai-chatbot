import time
import ctypes
import pygetwindow as gw
from typing import Optional

# Constants for commonly used keys (using scancodes)
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
        """Initialize the Actions class with an optional window title substring."""
        self.window_title_substring = window_title_substring

    @staticmethod
    def is_window_focused(title_substring):
        """Check if a window containing title_substring is currently focused."""
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

    def move_mouse(self, direction, distance: int=50, speed: float=1):
        """
        :param direction:
        :param distance:
        :param speed: A float between 0 (exclusive) and 1 (inclusive). 1 Means instant movement.
        :return:
        Move the mouse in a direction ('left', 'right') by a certain distance at a given speed.
        """

        # Validate the speed value
        if speed <= 0 or speed > 1:
            raise ValueError("Invalid speed value. Must be between 0 and 1 (exclusive).")

        # Calculate the delay based on the speed
        delay = 1 - speed

        if direction == 'left':
            step = -1  # Each segment moves left by 5 pixels
        else:
            step = 1  # Each segment moves right by 5 pixels

        for _ in range(distance):
            ctypes.windll.user32.mouse_event(0x0001, step, 0, 0, 0)
            time.sleep(delay / distance)  # Wait for the calculated amount of time between each segment


if __name__ == "__main__":
    actions = Actions(window_title_substring="NeosVR")
    while True:
        if actions.is_window_focused(actions.window_title_substring):
            print("Neos is focused")
            actions.turn_left()
            time.sleep(1)
            actions.turn_right()
            time.sleep(1)
            actions.move_forward()
            time.sleep(1)
            actions.move_back()
            time.sleep(1)
            actions.move_mouse('left', distance=300, speed=1)
            time.sleep(1)
            actions.move_mouse('right', distance=300, speed=1)
            time.sleep(1)
            actions.move_mouse('left', distance=300, speed=0.5)
            time.sleep(1)
            actions.move_mouse('right', distance=300, speed=0.5)
            time.sleep(1)
            actions.move_mouse('left', distance=300, speed=0.25)
            time.sleep(1)
            actions.move_mouse('right', distance=300, speed=0.25)
        time.sleep(1)
