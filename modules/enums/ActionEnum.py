from enum import Enum

class ActionEnum(Enum):
    MOVE_FORWARD = "move_forward"
    MOVE_BACK = "move_back"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    SHAKE_HEAD = "shake_head"
    NOD_HEAD = "nod_head"