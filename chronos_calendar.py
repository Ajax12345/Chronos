import typing, tigerSqlite, datetime
import re, calendar, chronos_utilities
import itertools

class _event_datetime(typing.NamedTuple):
    day:datetime.datetime
    timerange:str
    full_range:typing.List[datetime.datetime]

class _rangified:
    def __init__(self, _range:typing.List[datetime.datetime]) -> None:
        self._range = _range
    @classmethod
    def rangeify(cls, _payload:dict):
        return cls(Calendar.payload_to_range(_payload))
    def __iter__(self):
        yield from self._range

    def __eq__(self, _range) -> bool:
        if all(a == b for a, b in zip(self._range, _range)):
            return True
        if all(all(getattr(c, i) == getattr(d, i) for i in ['year', 'month', 'day', 'hour']) for c, d in zip(self._range, _range)) and all(abs(c.minutes - d.minutes) < 5 for c, d in zip(self._range, _range)): 
            return True
        return False


    

class Event:
    def __init__(self, _row:dict) -> None:
        self.__dict__ = _row
    @property
    def has_description(self):
        return bool(self.description)
    @property
    def condensed_title(self):
        return self.title if len(self.title) < 8 else self.title[:8]+'...'
    def __bool__(self):
        return True
    def __iter__(self):
        yield from [(a, b) for a, b in self.__dict__.items()]
    def __getitem__(self, _date:datetime.date) -> bool:
        return Calendar.event_datetime(dict(self)).day == _date
    @property
    def event_creation_date(self):
        _year, _month, _day, *_ = re.findall('\d+', self.created_on)
        return f'{Calendar.months[int(_month)-1]} {_day}, {_year}'
    
    @property
    def starttime(self):
        return re.findall('^\d+:\d+\s[APM]+', self.timerange)[0]
    def __eq__(self, _event) -> bool:
        _event1, _event2 = Calendar.event_datetime(dict(self)), Calendar.event_datetime(dict(_event)) 
        print('ranges')
        print(_event1.full_range, _event2.full_range)
        if all(a == b for a, b in zip(_event1.full_range, _event2.full_range)):
            return True
        a, b = _event1.full_range, _event2.full_range
        if all(all(getattr(c, i) == getattr(d, i) for i in ['year', 'month', 'day', 'hour']) for c, d in zip(a, b)) and abs(a[-1].day - b[-1].day) < 5:
            return True
        return False

class _event_wrapper:
    def __init__(self, _id:int, _event:Event, _time:datetime.datetime) -> None:
        self._event, self._time, self.id = _event, _time, _id
    def __getattr__(self, _attr:str) -> typing.Any:
        return getattr(self._event, _attr)
    @property
    def event_tag(self):
        class _tag:
            def __init__(self, _name:str) -> None:
                self.name = _name
            @property
            def color(self):
                return '#FABC09' if self.name == 'upcomming' else '#21DCAC'
        _d = personalEvents.event_rank_key({i:getattr(self, i) for i in ['timestamp', 'timerange']})
        return _tag('upcomming' if _d >= self._time else 'past event')    
        

class personalEvents:
    def __init__(self, _page:int, _flag:bool, _row:typing.List[dict]) -> None:
        self._row, self._page, self._flag = _row, _page, _flag
    @property
    def has_previous(self):
        return self._page > 0
    @property
    def has_next(self):
        return self._flag
    @property
    def next_page(self):
        if not self.has_next:
            raise ValueError('End of results')
        return self._page + 1
    @property
    def previous_page(self):
        if not self.has_previous:
            raise ValueError('start of results')
        return self._page - 1
    @staticmethod
    def event_rank_key(_payload:dict) -> datetime.datetime:
        _hour1, _minutes1, meridian1 = re.findall('\w+', _payload['timerange'].split(' - ')[0])
        return datetime.datetime(*map(int, _payload['timestamp'].split('-')), int(_hour1)+(0 if meridian1 == 'AM' else 12), int(_minutes1))
    def __iter__(self) -> typing.Generator:
        yield from self._row

    @classmethod
    def personal_events(cls, _user:int, _page:int = 0) -> typing.Callable:
        [_events] = [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if int(a) == int(_user)]
        new_events = sorted(_events, key=cls.event_rank_key, reverse=True)
        _groups = [new_events[i:i+5] for i in range(0, len(new_events), 5)]
        _d = datetime.datetime.now()
        return cls(_page, _page+1 < len(_groups), [_event_wrapper(i, Event(a), _d) for i, a in enumerate(_groups[_page], 1)]) 

class _events_on_day:
    def __init__(self, _day:datetime.date, _listing:typing.List[Event]) -> None:
        self._day, self.events = _day, _listing
    @property
    def day_num(self):
        return self._day.day
    def __bool__(self):
        return bool(self.events)
    @property
    def day(self):
        _calendar = list(calendar.Calendar().monthdatescalendar(self._day.year, self._day.month))
        [_week] = [i for i in _calendar if any(self._day == c for c in i)]
        return Calendar.days[[i for i, a in enumerate(_week) if a.day == self.day_num][0]]
    @property
    def month(self):
        return Calendar.months[self._day.month-1]
    
    def __iter__(self) -> typing.Generator:
        for i, a in enumerate(self.events):
            a.id_count = i
            yield a
        

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
        return 45 if not self.event else self.event.parent_height
    def __bool__(self):
        return bool(self.event)
    @property
    def div_id(self):
        return f'day_{self.day_val}_hour_{self.hour}'
    


    def __repr__(self):
        return f"Day(id={self.div_id}, height={self.height}, storing_event = {bool(self)})"

class _dayColumn:
    def __init__(self, _start:int, _day_info:_by_week_display, _events:list) -> None:
        self.header, self._is_starting = _day_info, _start
        self.events = sorted(_events, key=Calendar._event_sort_key)
    def __len__(self):
        return len(self.events)
    @property
    def is_start(self):
        return not self._is_starting
    @property
    def is_end(self):
        return self._is_starting == 6
    @property
    def inner_div_class(self):
        return ' '.join(i() for i in [lambda :'day_display', lambda :'is_today' if self.header.is_today else '', lambda :'start_corner' if self.is_start else '', lambda :'end_corner' if self.is_end else ''])
    @property
    def header_class(self):
        return ' '.join(i() for i in [lambda :'main_col', lambda :'' if not self.is_start else 'start_col'])
    def __iter__(self):
        start = 0
        _counter = itertools.count(1)
        for event in self.events:
            print('event here', event)
            hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|[AMP]+', event['timerange'])
            hour1, minutes1, hour2, minutes2 = int(hour1) if meridian1 == 'AM' else int(hour1) + 12, int(minutes1), int(hour2) if meridian2 == 'AM' else int(hour2)+12, int(minutes2)
            print('start before event', start)
            print('range values: ', hour1, start)
            for _ in range(hour1-start-1):
                yield _day_obj(self.header.rounded_day, next(_counter))
                start += 1
            print('start after event', start)
            
            _e = Event(event)
            _e.parent_height = 45*((hour2 if not minutes2 else hour2+1)-hour1)
            print('event minutes', minutes1)
            _e.from_top = int((minutes1/float(60))*45)
            print('from _top', _e.from_top)
            #_e.height = (45-_e.from_top)+((hour2-(hour1+1))*45)+(0 if not minutes2 else int((minutes2/float(60))*45))
            _e.height = (45-_e.from_top)+((hour2-(hour1+1))*45)+(0 if not minutes2 else int((minutes2/float(60))*45))
            print('height result: ', _e.height)
            yield _day_obj(self.header.rounded_day, next(_counter), event = _e)
            start += _e.parent_height//45
            print('final start', start)
            print('-'*20)
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
        self._week_row = [a for a, _ in self.full_data]
        self.__dict__.update({i:kwargs.get(i) for i in ['month', 'year', 'by_week']})
        print('kwargs in here', kwargs)
        print('month test here', self.month)
    @property
    def dayrange(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        return 'Monday {} - Sunday {}'.format(*self.__class__.singletion_dates(self.full_data))
    
    @property
    def previous_month(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        day1, day2 = self._week_row[0] - datetime.timedelta(days=7), self._week_row[-1] - datetime.timedelta(days=7)
        return Calendar.months[day1.month-1]

    @property
    def next_month(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        day1, day2 = self._week_row[0] + datetime.timedelta(days=7), self._week_row[-1] + datetime.timedelta(days=7)
        return Calendar.months[day1.month-1]

    @property
    def next_year(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        day1, day2 = self._week_row[0] + datetime.timedelta(days=7), self._week_row[-1] + datetime.timedelta(days=7)
        return day1.year

    @property
    def previous_year(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        day1, day2 = self._week_row[0] - datetime.timedelta(days=7), self._week_row[-1] - datetime.timedelta(days=7)
        return day1.year

    @property
    def previous_dayrange(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        day1, day2 = self._week_row[0] - datetime.timedelta(days=7), self._week_row[-1] - datetime.timedelta(days=7)
        #_day1, _day2 = day1 if day1 > 0 else (30 if self.previous_month in {'September', 'April', 'June', 'November'} else 31) - abs(day1), day2 if day2 > 0 else (30 if self.previous_month in {'September', 'April', 'June', 'November'} else 31) - abs(day2)
        return f'{day1.day}_{day2.day}'
    
    @property
    def next_dayrange(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        day1, day2 = self._week_row[0] + datetime.timedelta(days=7), self._week_row[-1] + datetime.timedelta(days=7)
        #_day1, _day2 = day1 if day1 > 0 else (30 if self.previous_month in {'September', 'April', 'June', 'November'} else 31) - abs(day1), day2 if day2 > 0 else (30 if self.previous_month in {'September', 'April', 'June', 'November'} else 31) - abs(day2)
        return f'{day1.day}_{day2.day}'

    @property
    def by_week_row(self):
        if not self.by_week:
            raise AttributeError('calendar instance by month, not week')
        return [_by_week_display(i, a) for i, [a, _] in enumerate(self.full_data)]

    def __iter__(self):
        if self.by_week:
            for i, [[_, b], c] in enumerate(zip(self.full_data, self.by_week_row)):
                yield _dayColumn(i, c, b)
    
    @staticmethod
    def singletion_dates(_data:list) -> str:
        _prefixes = {1:'st', 2:'nd', 3:'rd'}
        _start, *_, _end = [a for a, _ in _data]
        return [f"{_start.day}{_prefixes.get(_start.day, 'th')}", f"{_end.day}{_prefixes.get(_end.day, 'th')}"]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(by_week={True if self.by_week else False}, month={self.month}, year={self.year}, dayrange={None if not self.by_week else self.dayrange})'
    
    @classmethod
    def event_datetime(cls, _event:dict) -> datetime.datetime:
        print('got event here', _event)
        day, _hour = map(int, re.findall('\d+', _event['parent_id']))
        _start, _end = map(int, re.findall('\d+', _event['week_range']))
        full_calendar = calendar.Calendar().monthdatescalendar(int(_event['year']), cls.months.index(_event['month'])+1)
        full_day = [i for i in full_calendar if i[0].day == _start and i[-1].day == _end][0][day-1]
        hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|[APM]+', _event['timerange'])
        full_timerange = [datetime.datetime(*[*[getattr(full_day, i) for i in ['year', 'month', 'day']], int(hour1)+(0 if meridian1 == 'AM' else 12), int(minutes1)]), datetime.datetime(*[*[getattr(full_day, i) for i in ['year', 'month', 'day']], int(hour2)+(0 if meridian2 == 'AM' else 12), int(minutes2)])]
        return _event_datetime(full_day, _event['timerange'], full_timerange)
    
    @classmethod
    def _event_sort_key(cls, _event:dict) -> typing.Tuple[int, int]:
        '''
        hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|[APM]+', _event['timerange'])
        return (int(hour1)+(0 if meridian1 == 'AM' else 12)+int(minutes1), int(hour2)+(0 if meridian2 == 'AM' else 12)+int(minutes2))
        '''
        hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|[APM]+', _event['timerange'])
        return [(int(hour1)+(0 if meridian1 == 'AM' else 12), int(minutes1)), (int(hour2)+(0 if meridian2 == 'PM' else 12), int(minutes2))]
    @classmethod
    def create_calendar_event(cls, _user:int, _payload:dict) -> None:
        _timestamps = cls.event_datetime(_payload)
        print('event creation payload', _payload)
        new_payload = {'timestamp':str(_timestamps.day), 'created_on':str(datetime.datetime.now()), **_payload}
        print('resulting payload', new_payload)
        current_events = [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if a == _user][-1]
        tigerSqlite.Sqlite('user_calendars.db').update('calendars', [['events', sorted(current_events+[new_payload], key=cls._event_sort_key)]], [['id', _user]])
        
    @classmethod
    def quick_look(cls, _user:int, _payload:dict) -> typing.Callable:
        _user_events = list(map(Event, [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if a == _user][-1]))
        return [i for i in _user_events if i == Event(_payload)][0]

    @classmethod
    @chronos_utilities.rangeify
    def by_week(cls, _user:int, _week:typing.List[datetime.date]) -> typing.Callable:
        _all_events =[b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if int(a) == int(_user)][0]
        _ranges = [[i, [a for a in _all_events if datetime.date(*map(int, re.findall('\d+', a['timestamp']))) == i]] for i in _week]
        return cls(_ranges, by_week = True, year=_week[-1].year, month=cls.months[_week[-1].month-1])

    @classmethod
    def _by_week(cls, _user:int, _week:typing.List[datetime.date], year:int, month:str) -> typing.Callable:
        _all_events =[b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if int(a) == int(_user)][0]
        _ranges = [[i, [a for a in _all_events if datetime.date(*map(int, re.findall('\d+', a['timestamp']))) == i]] for i in _week]
        return cls(_ranges, by_week = True, year=year, month=month)

    @classmethod
    def remove_event(cls, _user:int, _payload:dict) -> typing.Callable:
        _all_events =[b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if int(a) == int(_user)][0]
        new_events = [i for i in _all_events if Event(i) != Event(_payload)]
        tigerSqlite.Sqlite('user_calendars.db').update('calendars', [['events', new_events]], [['id', int(_user)]])
        return cls.by_week(user=_user, expedient=True)
    
    @classmethod
    def navigate_week(cls, _user:int, payload:dict) -> typing.Callable:
        _calendar = calendar.Calendar().monthdatescalendar(int(payload['year']), cls.months.index(payload['month'])+1)
        _day1, _day2 = map(int, re.findall('\d+', payload['dayrange']))
        _new_week = [i for i in _calendar if i[0].day == _day1 and i[-1].day == _day2][0]
        return cls._by_week(_user, _new_week, int(payload['year']), payload['month'])


    @classmethod
    @chronos_utilities.to_datetime
    def events_by_day(cls, _user:int, _day:datetime.date) -> _events_on_day:
        [_event] = [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if int(a) == int(_user)]
        return _events_on_day(_day, [Event(i) for i in _event if Event(i)[_day]])


    @classmethod
    def payload_to_range(cls, _payload:dict) -> typing.List[datetime.datetime]:
        hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('^\d+(?=:)|(?<=:)\d+|[AMP]+(?=\s)|(?<=\s)\d+(?=:)|[AMP]+(?=$)', _payload['timerange'])
        hour1, minutes1, hour2, minutes2 = int(hour1) + (0 if meridian1 == 'AM' else 12), int(minutes1), int(hour2)+(0 if meridian2 == 'AM' else 12), int(minutes2)
        return [datetime.datetime(*map(int, _payload['timestamp'].split('-')), hour1, minutes1), datetime.datetime(*map(int, _payload['timestamp'].split('-')), hour2, minutes2)]
    
    @classmethod
    @chronos_utilities.to_range
    def from_pannel_view(cls, _user:int, _range:typing.List[datetime.date]) -> Event:
        [_events] = [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if int(a) == int(_user)]
        return [Event(i) for i in _events if _rangified.rangeify(i) == _rangified(_range)][0]

    @classmethod
    def navigate_by_week(cls, _user:int, _payload:dict) -> typing.Callable:
        day1, day2 = map(int, re.findall('\d+', _payload['dayrange']))
        _current_month = cls.months.index(_payload['month'])+1
        if _payload['direction'] == 'backward':
            _day1, _day2 = day1-7, day2-7
            if _day1 > 0 and _day2 > 0:
                new_calendar = calendar.Calendar().monthdatescalendar(int(_payload['year']), _current_month)
                new_result = [i for i in new_calendar if i[0].day == _day1 and i[-1].day == _day2][0]
                return cls.by_week.__wrapped__(cls, _user, new_result)
            _new_month = 'December' if _current_month == 'January' else cls.months[_current_month-2]
            print(_new_month)
            _new_year = int(_payload['year']) - 1 if _current_month == 'January' else int(_payload['year'])
            _day_1, _day_2 = (30 if _new_month in {'April', 'June', 'November', 'September'} else 31)- abs(_day1) if _day1 <= 0 else _day1, (30 if _new_month in {'April', 'June', 'November', 'September'} else 31)- abs(_day2) if _day2 <= 0 else _day2
            print(_day_1, _day_2)
            new_calendar = calendar.Calendar().monthdatescalendar(_new_year, cls.months.index(_new_month) + 1)
            return cls._by_week(_user, [i for i in new_calendar if i[0].day == _day_1 and i[-1].day == _day_2][0], _new_year, _new_month)
        '''
        print(day1, day2, _current_month)
        if _payload['direction'] == 'forward':
            if day1 > day2:
                new_calendar = calendar.Calendar().monthdatescalendar(int(_payload['year']) if _current_month != 12 else int(_payload['year'])+1, _current_month + 1 if _current_month != 12 else 1)
                print('week row new 1', new_calendar[0])
                return cls._by_week(_user, new_calendar[0], int(_payload['year']) if _current_month != 12 else int(_payload['year'])+1, cls.months[(_current_month + 1 if _current_month != 12 else 1) - 1])
            
            new_calendar = calendar.Calendar().monthdatescalendar(int(_payload['year']), _current_month)
            _ind = [i for i, a in enumerate(new_calendar) if a[0].day == day1 and a[-1].day == day2][0]
            print('week row new 2', new_calendar[_ind+1])
            return cls._by_week(_user, new_calendar[_ind+1], int(_payload['year']), cls.months[_current_month-1])
    
        if day1 > day2 or day1 == 1:
            new_calendar = calendar.Calendar().monthdatescalendar(int(_payload['year']) if _current_month != 1 else int(_payload['year'])-1, _current_month - 1 if _current_month != 1 else 12)
            print(_current_month)
            print('week row new 3', new_calendar[-1])
            return cls._by_week(_user, new_calendar[-1], int(_payload['year']) if _current_month != 1 else int(_payload['year'])-1, cls.months[(_current_month - 1 if _current_month != 1 else 12)-1])

        new_calendar = calendar.Calendar().monthdatescalendar(int(_payload['year']), _current_month)
        _ind = [i for i, a in enumerate(new_calendar) if a[0].day == day1 and a[-1].day == day2][0]
        print('week row new 4', new_calendar[_ind-1])
        return cls._by_week(_user, new_calendar[_ind-1], int(_payload['year']), cls.months[_current_month-1])
        '''
