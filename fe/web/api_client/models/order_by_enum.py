from enum import Enum


class OrderByEnum(str, Enum):
    LIKES = "likes"
    PREFERENCES = "preferences"
    TIMESTAMP = "timestamp"

    def __str__(self) -> str:
        return str(self.value)
