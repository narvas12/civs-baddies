from enum import Enum

class RatingTag(Enum):
    WORSE = 1
    BAD = 2
    GOOD = 3
    GREAT = 4
    EXCELLENT = 5
    
    @classmethod
    def get_key_by_value(cls, value):
        for name, member in cls.__members__.items():
            if member.value == value:
                return name
        raise ValueError("Invalid value for status")
    
    @classmethod
    def enum_has_value(cls, value):
        for name, member in cls.__members__.items():
            if member.value == value:
                return True
           
        return False
    
  