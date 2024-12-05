
import enum

class ParsingResult(enum.Enum):
    FAILED  = 0
    IGNORED = 1
    SUCCESS = 2

    def is_failed  (self) -> bool:
        return self == ParsingResult.FAILED
    def is_ignored (self) -> bool:
        return self == ParsingResult.IGNORED
    def is_success (self) -> bool:
        return self == ParsingResult.SUCCESS
