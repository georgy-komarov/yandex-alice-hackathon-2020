from enum import Enum


class State(Enum):
    SEND_CODE = 0
    WAIT_FOR_CODE = 1
    READY = 2
    START = 3
    ACTION = 4
    
State.ALL = tuple(State)

