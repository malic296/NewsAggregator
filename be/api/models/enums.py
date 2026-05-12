from enum import Enum

class OrderByEnum(str, Enum):
    LIKES = "likes"
    TIMESTAMP = "timestamp"
    PREFERENCES = "preferences"