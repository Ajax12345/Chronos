import typing, tigerSqlite, datetime
import re, calendar, chronos_utilities
import itertools

class _event_datetime(typing.NamedTuple):
    day:datetime.datetime
    timerange:str
    full_range:typing.List[datetime.datetime]

class Event:
    def __init__(self, _row:dict) -> None:
        self.__dict__ = _row
    @property
    def has_description(self):
        return bool(self.description)
    def __bool__(self):
        return True
    def __iter__(self):
        yield from [(a, b) for a, b in self.__dict__.items()]
    def __eq__(self, _event) -> bool:
        _event1, _event2 = Calendar.event_datetime(dict(self)), Calendar.event_datetime(_event) 
        return all(a == b for a, b in zip(_event1.full_range, _event2.full_range))

class _by_week_display:
    def __init__(self, _day_id:int, _day:datetime.date) -> None:
        self.day_id, self.full_day = _day_id, _day
        self._d = datetime.datetime.now()
    @property
    def day_abbrev(self):
        return Calendar.days[self.day_id][:3]
    @property
    def day_num(self):
        return self.full_day.day
    
    @property
    def rounded_day(self):
        return self.day_id+1

    @property
    def is_in_month(self):
        return self._d.month == self.full_day.month

    @property
    def is_today(self):
        return all(getattr(self._d, i) == getattr(self.full_day, i) for i in ['year', 'month', 'day'])

    def __repr__(self):
        return f'<{self.day_abbrev} {self.day_num}, is_today={self.is_today}>'

class _day_obj:
    def __init__(self, _day_val:int, _hour:int, **kwargs:dict) -> None:
        self.day_val, self.hour, self.event= _day_val, _hour, kwargs.get('event')
    @property
    def height(self):
        return 45 if not self.event else self.event.height
    def __bool__(self):
        return bool(self.event)
    @property
    def div_id(self):
        return f'day_{self.day_val}_hour_{self.hour}'

    def __repr__(self):
        return f"Day(id={self.div_id}, height={self.height}, storing_event = {bool(self)})"

class _dayColumn:
    def __init__(self, _day_info:_by_week_display, _events:list) -> None:
        self.header = _day_info
        self.events = _events
    def __len__(self):
        return len(self.events)
    def __iter__(self):
        start = 0
        _counter = itertools.count(1)
        for event in self.events:
            hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|[AMP]+', event['timerange'])
            hour1, minutes1, hour2, minutes2 = int(hour1) if meridian1 == 'AM' else int(hour1) + 12, int(minutes1), int(hour2) if meridian2 == 'AM' else int(hour2)+12, int(minutes2)
            for _ in range(start, hour1+start):
                yield _day_obj(self.header.rounded_day, next(_counter))
            _e = Event(event)
            _e.height = 45*((hour2 if not minutes2 else hour2+1)-hour1)
            yield _day_obj(self.header.rounded_day, next(_counter), event = _e)
            start += _e.height//45
        for _ in range(start, 24):
            yield _day_obj(self.header.rounded_day, next(_counter))
    
    def __repr__(self) -> str:
        return f'dayColumn({self.header}, event_num = {len(self)})'


class Calendar:
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    """
    filename: user_calendars.db
    tablename: calendars
    columns: id real, events text
    """
    def __init__(self, _data:list, **kwargs:dict) -> None:
        self.full_data = _data
        self.__dict__.update({i:kwargs.get(i) for i in ['month', 'year', 'by_week']})
        
    @property
    def dayrange(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        return 'Monday {} - Sunday {}'.format(*self.__class__.singletion_dates(self.full_data))
    

    @property
    def by_week_row(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        return [_by_week_display(i, a) for i, [a, _] in enumerate(self.full_data)]

    def __iter__(self):
        if self.by_week:
            for [_, b], c in zip(self.full_data, self.by_week_row):
                yield _dayColumn(c, b)
    
    @staticmethod
    def singletion_dates(_data:list) -> str:
        _prefixes = {1:'st', 2:'nd', 3:'rd'}
        _start, *_, _end = [a for a, _ in _data]
        return [f"{_start.day}{_prefixes.get(_start.day, 'th')}", f"{_end.day}{_prefixes.get(_end.day, 'th')}"]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(by_week={True if self.by_week else False}, month={self.month}, year={self.year}, dayrange={None if not self.by_week else self.dayrange})'
    
    @classmethod
    def event_datetime(cls, _event:dict) -> datetime.datetime:
        day, _hour = map(int, re.findall('\d+', _event['parent_id']))
        _start, _end = map(int, re.findall('\d+', _event['week_range']))
        full_calendar = calendar.Calendar().monthdatescalendar(int(_event['year']), cls.months.index(_event['month'])+1)
        full_day = [i for i in full_calendar if i[0].day == _start and i[-1].day == _end][0][day-1]
        hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|[APM]+', _event['timerange'])
        full_timerange = [datetime.datetime(*[*[getattr(full_day, i) for i in ['year', 'month', 'day']], int(hour1)+(0 if meridian1 == 'AM' else 12), int(minutes1)]), datetime.datetime(*[*[getattr(full_day, i) for i in ['year', 'month', 'day']], int(hour2)+(0 if meridian2 == 'AM' else 12), int(minutes2)])]
        return _event_datetime(full_day, _event['timerange'], full_timerange)
    
    @classmethod
    def create_calendar_event(cls, _user:int, _payload:dict) -> None:
        _timestamps = cls.event_datetime(_payload)
        new_payload = {'timestamp':str(_timestamps.day), 'created_on':str(datetime.datetime.now()), **_payload}
        print('resulting payload', new_payload)
        current_events = [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if a == _user][-1]
        tigerSqlite.Sqlite('user_calendars.db').update('calendars', [['events', current_events+[new_payload]]], [['id', _user]])
        
    @classmethod
    def quick_look(cls, _user:int, _payload:dict) -> typing.Callable:
        _user_events = list(map(Event, [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if a == _user][-1]))
        return [Event(i) for i in _user_events if i == Event(_payload)][0]

    @classmethod
    @chronos_utilities.rangeify
    def by_week(cls, _user:int, _week:typing.List[datetime.date]) -> typing.Callable:
        _all_events =[b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if int(a) == int(_user)][0]
        _ranges = [[i, [a for a in _all_events if datetime.date(*map(int, re.findall('\d+', a['timestamp']))) == i]] for i in _week]
        return cls(_ranges, by_week = True, year=_week[-1].year, month=_week[-1].year)
