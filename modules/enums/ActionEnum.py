from enum import Enum

class ActionEnum(Enum):
    MOVE_FORWARD = "move_forward"
    MOVE_BACK = "move_back"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    SHAKE_HEAD = "shake_head"
    NOD_HEAD = "nod_head"
    TURN_AROUND = "turn_around"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    TURN_LEFT_UNTIL_STOP_FLAG = "turn_left_until_stop_flag"
    TURN_RIGHT_UNTIL_STOP_FLAG = "turn_right_until_stop_flag"
