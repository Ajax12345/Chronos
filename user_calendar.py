import typing, tigerSqlite, datetime
import re, calendar

class _event_datetime(typing.NamedTuple):
    day:datetime.datetime
    timerange:str
    full_range:typing.List[datetime.datetime]

class Event:
    def __init__(self, _row:dict) -> None:
        self.__dict__ = _row
    def __eq__(self, _event) -> bool:
        pass

class Calendar:
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    """
    filename: user_calendars.db
    tablename: calendars
    columns: id real, events text
    """
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
        day, _hour = map(int, re.findall('\d+', _payload['parent_id']))
        _start, _end = map(int, re.findall('\d+', _payload['week_range']))
        full_calendar = calendar.Calendar().monthdatescalendar(int(_payload['year']), cls.months.index(_payload['month'])+1)
        full_day = [i for i in full_calendar if i[0].day == _start and i[-1].day == _end][0][day-1]
        new_payload = {'timestamp':str(full_day), 'created_on':str(datetime.datetime.now()), **_payload}
        current_events = [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if a == _user][-1]
        tigerSqlite.Sqlite('user_calendars.db').update('calendars', [['events', current_events+[new_payload]], [['id', _user]]])
        
    @classmethod
    def quick_look(cls, _user:int, _payload:dict) -> typing.Callable:
        _user_events = [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if a == _user][-1]
