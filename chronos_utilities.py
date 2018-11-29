import tigerSqlite, sqlite3, typing
import datetime

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