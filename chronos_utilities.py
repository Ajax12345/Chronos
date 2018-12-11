import tigerSqlite, sqlite3, typing, re
import datetime, calendar, functools

def validate_parameters(_f:typing.Callable[[typing.Callable, dict], typing.Callable]) -> typing.Callable:
    def _wrapper(_cls, **_kwargs) -> typing.Any:
        return {'success':'False'} if not any((lambda x:all(x[i] == _kwargs[i] for i in _kwargs))(dict(zip(_cls.headers, h))) for h in tigerSqlite.Sqlite('user_credentials.db').get_id_name_email_password_settings('credentials')) else _f(_cls, **_kwargs)

    return _wrapper


def parse_datetime(_f:typing.Callable) -> typing.Callable:
    def _wrapper(cls, **kwargs):
        if not kwargs:
            _d = datetime.datetime.now()
            return _f(cls, _d.month, _d.year)
        month, year = cls.month_converter(kwargs['month']) if not isinstance(kwargs['month'], int) else kwargs['month'], int(kwargs['year']) if not isinstance(kwargs['year'], int) else kwargs['year']
        return _f(cls, 12 if month < 1 else 1 if month > 12 else month, year - 1 if month < 1 else year + 1 if month > 12 else year)

    return _wrapper

def _parse_year_day(_payload:dict) -> typing.Tuple[int, int]:
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return int(_payload['year']) if isinstance(_payload['year'], str) else _payload['year'], months.index(_payload['month'])+1 if isinstance(_payload['month'], str) else _payload['month']

def rangeify(_f:typing.Callable) -> typing.Callable:
    @functools.wraps(_f)
    def _wrapper(_cls, **kwargs:dict) -> typing.Callable:
        if 'user' not in kwargs:
            raise TypeError(f'"{_f.__name__}" requires a user id')
        if kwargs.get('expedient', False):
            _d = datetime.datetime.now()
            _new_d = datetime.date(*[getattr(_d, i) for i in ['year', 'month', 'day']])
            _week = [i for i in calendar.Calendar().monthdatescalendar(_d.year, _d.month) if any(c == _new_d for c in i)][0]
            return _f(_cls, kwargs.get('user'), _week)
        _day1, _day2 = map(int, re.findall('\d+', kwargs['dayrange']))
        _week = [i for i in calendar.Calendar().monthdatescalendar(*_parse_year_day(kwargs)) if i[0].day == _day1 and i[-1].day == _day2][0]
        return _f(_cls, kwargs.get('user'), _week)
    return _wrapper

