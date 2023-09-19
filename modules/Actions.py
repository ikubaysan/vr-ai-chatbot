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
        self.window_is_focused = self.is_window_focused(self.window_title)
        self.action_queue = deque()
        self.thread = None
        self.window_focus_thread = None
        self.stop_flag = False

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._execute_actions)
            self.thread.start()
            logger.info(f"Started Actions thread")
        if self.window_focus_thread is None:
            self.window_focus_thread = threading.Thread(target=self._check_window_focus)
            self.window_focus_thread.start()
            logger.info(f"Started window focus thread")

    def _check_window_focus(self):
        while True:
            self.window_is_focused = self.is_window_focused(self.window_title)
            time.sleep(0.01)

    def enqueue_action(self, action: ActionEnum):
        self.action_queue.append(action)
        logger.info(f"Enqueued action: {action.value}")

    def _execute_actions(self):
        while True:
            if self.window_is_focused:
                while self.action_queue and self.window_is_focused:
                    if self.stop_flag:
                        logger.info(f"Stop flag set, clearing action queue")
                        self.action_queue.clear()
                        self.stop_flag = False
                        break
                    action = self.action_queue.popleft()
                    getattr(self, action.value)()
                    logger.info(f"Executed action: {action.value}")
            else:
                self.action_queue.clear()
                self.stop_flag = False
            time.sleep(0.001)

    @staticmethod
    def is_window_focused(title: str):
        """Check if a window with the title is currently focused."""
        try:
            active_window = gw.getActiveWindow()
            #return title.lower() in active_window.title.lower()
            return title.lower() == active_window.title.lower()
        except Exception as e:
            print(f"An error occurred in is_window_focused(): {e}")
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

    def move_forward(self, duration: float = 0.5, do_until_stop_flag: bool = False):
        if do_until_stop_flag:
            while self.stop_flag is False and self.window_is_focused:
                self.press_and_release_key(W, duration)
                time.sleep(0.5)
        else:
            self.press_and_release_key(W, duration)

    def move_back(self, duration: float = 0.5, do_until_stop_flag: bool = False):
        if do_until_stop_flag:
            while self.stop_flag is False and self.window_is_focused:
                self.press_and_release_key(S, duration)
                time.sleep(0.5)
        else:
            self.press_and_release_key(S, duration)

    def move_left(self, duration: float = 0.5):
        self.press_and_release_key(A, duration)

    def move_right(self, duration: float = 0.5):
        self.press_and_release_key(D, duration)

    def press_and_release_key(self, hex_key_code, duration: float = 0.5):
        self.press_key(hex_key_code)
        time.sleep(duration)
        self.release_key(hex_key_code)

    def move_mouse(self, direction, distance: int = 50, duration: float = 1):
        """
        :param direction: The direction to move the mouse ('left', 'right', 'up', 'down')
        :param distance: The distance to move the mouse.
        :param duration: Total time in seconds it should take to move the mouse the specified distance.
        :return: None
        """
        if duration <= 0:
            raise ValueError("Invalid duration value. Must be greater than 0.")

        step_delay = duration / distance  # Time to sleep between each step
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
            if self.stop_flag:
                logger.info(f"Stop flag set, so early exiting move_mouse()")
                return
            elif not self.window_is_focused:
                logger.info(f"Window is no longer focused, so early exiting move_mouse()")
                return
            ctypes.windll.user32.mouse_event(0x0001, step_x, step_y, 0, 0)
            time.sleep(step_delay)

    def move_mouse_left(self, distance: int = 50, duration: float = 1, do_until_stop_flag: bool = False):
        if do_until_stop_flag:
            while self.stop_flag is False and self.window_is_focused:
                self.move_mouse('left', distance, duration)
        else:
            self.move_mouse('left', distance, duration)

    def move_mouse_right(self, distance: int = 50, duration: float = 1, do_until_stop_flag: bool = False):
        if do_until_stop_flag:
            while self.stop_flag is False and self.window_is_focused:
                self.move_mouse('right', distance, duration)
        else:
            self.move_mouse('right', distance, duration)

    def move_mouse_up(self, distance: int = 50, duration: float = 1):
        self.move_mouse('up', distance, duration)

    def move_mouse_down(self, distance: int = 50, duration: float = 1):
        self.move_mouse('down', distance, duration)

    def nod_head(self):
        self.move_mouse_up(distance=250, duration=0.05)
        self.move_mouse_down(distance=500, duration=0.1)
        self.move_mouse_up(distance=250, duration=0.05)

    def shake_head(self):
        self.move_mouse_left(distance=250, duration=0.05)
        self.move_mouse_right(distance=500, duration=0.1)
        self.move_mouse_left(distance=250, duration=0.05)

    def turn_right(self):
        self.move_mouse_right(distance=500, duration=5)

    def turn_left(self):
        self.move_mouse_left(distance=500, duration=5)

    def turn_right_until_stop_flag(self):
        self.move_mouse_right(do_until_stop_flag=True)

    def turn_left_until_stop_flag(self):
        self.move_mouse_left(do_until_stop_flag=True)

    def move_forward_until_stop_flag(self):
        self.move_forward(duration=1, do_until_stop_flag=True)

    def move_back_until_stop_flag(self):
        self.move_back(duration=1, do_until_stop_flag=True)


if __name__ == "__main__":
    #actions = Actions(window_title="NeosVR")
    actions = Actions(window_title="VRChat")
    actions.start()

    while True:
        if actions.window_is_focused:
            print("Game is focused")
            #actions.enqueue_action(ActionEnum.TURN_AROUND)
            # actions.enqueue_action(ActionEnum.NOD_HEAD)
            # actions.enqueue_action(ActionEnum.NOD_HEAD)
            time.sleep(2)
            # actions.enqueue_action(ActionEnum.SHAKE_HEAD)
            # actions.enqueue_action(ActionEnum.SHAKE_HEAD)

            #actions.enqueue_action(ActionEnum.TURN_LEFT)
            #actions.enqueue_action(ActionEnum.TURN_RIGHT)

            actions.enqueue_action(ActionEnum.TURN_RIGHT_UNTIL_STOP_FLAG)

        time.sleep(3)