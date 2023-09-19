import time
import ctypes
import pygetwindow as gw
import threading
from typing import Optional
from collections import deque
from enum import Enum
from modules.helpers.logging_helper import logger
from modules.enums.ActionEnum import ActionEnum

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
    def __init__(self, window_title: Optional[str] = None):
        """Initialize the Actions class with an optional window title substring."""
        if not window_title:
            raise ValueError("A window title is required.")
        self.window_title = window_title
        self.action_queue = deque()
        self.thread = None

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._execute_actions)
            self.thread.start()

    def enqueue_action(self, action: ActionEnum):
        self.action_queue.append(action)
        logger.info(f"Enqueued action: {action.value}")


    def _execute_actions(self):
        while True:
            if self.is_window_focused(self.window_title):
                while self.action_queue:
                    action = self.action_queue.popleft()
                    getattr(self, action.value)()
                    logger.info(f"Executed action: {action.value}")
            else:
                # Clear the queue if the window is not focused
                self.action_queue.clear()

            time.sleep(1)

    @staticmethod
    def is_window_focused(title: str):
        """Check if a window with the title is currently focused."""
        try:
            active_window = gw.getActiveWindow()
            return title.lower() in active_window.title.lower()
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

    def move_mouse(self, direction, distance: int = 50, speed: float = 1):
        """
        :param direction: The direction to move the mouse ('left', 'right', 'up', 'down')
        :param distance: The distance to move the mouse.
        :param speed: A float between 0 (exclusive) and 1 (inclusive). 1 means instant movement.
        :return: None
        """
        if speed <= 0 or speed > 1:
            raise ValueError("Invalid speed value. Must be between 0 and 1 (exclusive).")

        delay = 1 - speed
        step_x, step_y = 0, 0

        if direction == 'left':
            step_x = -1
        elif direction == 'right':
            step_x = 1
        elif direction == 'up':
            step_y = -1
        elif direction == 'down':
            step_y = 1
        else:
            raise ValueError("Invalid direction. Must be 'left', 'right', 'up', or 'down'.")

        for _ in range(distance):
            ctypes.windll.user32.mouse_event(0x0001, step_x, step_y, 0, 0)
            time.sleep(delay / distance)

    def move_mouse_left(self, distance: int = 50, speed: float = 1):
        self.move_mouse('left', distance, speed)

    def move_mouse_right(self, distance: int = 50, speed: float = 1):
        self.move_mouse('right', distance, speed)

    def move_mouse_up(self, distance: int = 50, speed: float = 1):
        self.move_mouse('up', distance, speed)

    def move_mouse_down(self, distance: int = 50, speed: float = 1):
        self.move_mouse('down', distance, speed)

    def nod_head(self):
        self.move_mouse_up(distance=250, speed=0.999)
        self.move_mouse_down(distance=500, speed=0.999)
        self.move_mouse_up(distance=250, speed=0.999)

    def shake_head(self):
        self.move_mouse_left(distance=250, speed=0.999)
        self.move_mouse_right(distance=500, speed=0.999)
        self.move_mouse_left(distance=250, speed=0.999)


if __name__ == "__main__":
    actions = Actions(window_title="NeosVR")
    actions.start()

    while True:
        if actions.is_window_focused(actions.window_title):
            print("Neos is focused")
            actions.enqueue_action(ActionEnum.SHAKE_HEAD)
        time.sleep(1)