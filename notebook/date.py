ENABLE_WEEKDAYS = False
ENABLE_SUBDAY_DATES = False
ENABLE_RELATIVE_DATES = True

from enum import StrEnum, auto


class Date(StrEnum):
    now = auto()
    second = auto()
    minute = auto()
    hour = auto()
    day = auto()
    weekday = auto()
    week = auto()
    month = auto()
    year = auto()
    yesterday = auto()
    today = auto()
    tomorrow = auto()

    @property
    def offset_in_days(self) -> int:
        if self is Date.yesterday:
            return -1
        elif self is Date.tomorrow:
            return +1
        else:
            return 0

    @property
    def format_string(self) -> str:
        if self in [Date.second, Date.now]:
            return "%Y-%m-%dT%H:%M:%S"
        if self is Date.minute:
            return "%Y-%m-%dT%H:%M"
        if self is Date.hour:
            return "%Y-%m-%dT%H"
        elif self in [
            Date.day,
            Date.week,
            Date.yesterday,
            Date.today,
            Date.tomorrow,
        ]:
            return "%Y-%m-%d"
        elif self is Date.week:
            return "%Y-W%V"
        elif self is Date.weekday:
            return "%Y-W%V-%w"  # %V is iso, %U from sunday, %W from monday
        elif self is Date.month:
            return "%Y-%m"
        elif self is Date.year:
            return "%Y"
        else:
            raise ValueError("format of variable `date` is not valid")

    @classmethod
    def choices(cls) -> list[str]:
        date_choices = [choice for choice in Date]
        unwanted = []
        if not ENABLE_SUBDAY_DATES:
            unwanted.extend([Date.second, Date.minute, Date.hour])
        if not ENABLE_WEEKDAYS:
            unwanted.extend([Date.week, Date.weekday])
        if not ENABLE_RELATIVE_DATES:
            unwanted.extend([Date.now, Date.yesterday, Date.today, Date.tomorrow])
        return [choice for choice in date_choices if choice not in unwanted]
