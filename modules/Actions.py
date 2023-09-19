import pyautogui
import time
import pygetwindow as gw
from typing import Optional, Tuple

class Actions:

    def __init__(self, window_title_substring: Optional[str] = None):
        self.window_title_substring = window_title_substring
        return

    @staticmethod
    def is_window_focused(title_substring):
        try:
            active_window = gw.getActiveWindow()
            return title_substring.lower() in active_window.title.lower()
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def move_forward(self):
        pyautogui.press('w')
        time.sleep(0.5)
        pyautogui.press('w')

    def turn_left(self):
        pyautogui.press('a')
        time.sleep(0.5)
        pyautogui.press('a')


if __name__ == "__main__":
    actions = Actions(window_title_substring="NeosVR")
    while True:
        if actions.is_window_focused(actions.window_title_substring):
            print("Neos is focused")
            actions.move_forward()
        time.sleep(1)

