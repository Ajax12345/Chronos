import calendar, re, typing
import datetime, chronos_utilities

class Day:
    def __init__(self, _day:datetime.datetime, _month:int, _year:int, _now:datetime.datetime) -> None:
        self.day, self.month, self.year, self.now = _day, _month, _year, _now
    def __repr__(self):
        return '-'.join(str(getattr(self.day, i)) for i in ['month', 'day', 'year'])
    @property
    def day_num(self):
        return self.day.day
    @property
    def class_attr(self):
        if self.day.day == self.now.day and self.now.month == self.month and self.day.month == self.month:
            return 'today'
            
        return 'ignore_date' if self.day.month != self.month else 'today_day'
    @property
    def attr_class(self):
        if self.day.day == self.now.day and self.now.month == self.month and self.day.month == self.month:
            return 'today'

        if self.now.month == self.month and self.day.day < self.now.day and self.day.month == self.now.month:
            return 'previous_day'
        
        return 'ignore_date' if self.day.month != self.month else 'today_day'
class Week:
    def __init__(self, _week:typing.List[datetime.datetime], _month:int, _year:int, _current:datetime.datetime.now) -> None:
        self.week, self.month, self.year = _week, _month, _year
        self.now = _current
    def __iter__(self):
        for day in self.week:
            yield Day(day, self.month, self.year, self.now)

class Calendar:
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    def __init__(self, _full_month:typing.List[typing.List[datetime.datetime]], _year:int, _month:int, _current_moment:datetime.datetime.now) -> None:
        self.full_month, self.year, self.month = _full_month, _year, _month
        self.now = _current_moment
    @property
    def text_month(self):
        return self.__class__.months[self.month-1]

    def __bool__(self):
        return self.month > self.now.month or self.year > self.now.year


    def __iter__(self):
        for week in self.full_month:
            yield Week(week, self.month, self.year, self.now)
  
    @classmethod
    @chronos_utilities.parse_datetime
    def full_calendar(cls, _month:int, _year:int) -> typing.Callable:
        return cls(calendar.Calendar().monthdatescalendar(_year, _month), _year, _month, datetime.datetime.now())

    @classmethod
    def mini_calendar(cls, _timestamp:str) -> typing.Callable:
        year, month, day = map(int, re.findall('\d+', _timestamp))
        return cls(calendar.Calendar().monthdatescalendar(year, month), year, month, datetime.date(year, month, day))

    @classmethod
    def month_converter(cls, _month:str) -> int:
        return dict(zip(map(str.lower, cls.months), range(1, 13)))[_month.lower()]
    
