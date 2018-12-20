import tigerSqlite, sqlite3, typing
import datetime

class _group:
    def __init__(self, _id:int, _payload:dict) -> None:
        self.id = _id
        self.__dict__.update(_payload)
    

class Groups:
    """
    filename: user_groups.db
    tablename: groups 
    columns: id real, listings text
    """
    def __init__(self, _row:typing.List[dict]) -> None:
        self.groups = _row
    def __bool__(self):
        return bool(self.groups)
    def __iter__(self):
        for i, a in enumerate(self.groups, 1):
            yield _group(i, a)
    @classmethod
    def user_groups(cls, _user:int) -> None:
        [_groups] = [b for a, b in tigerSqlite.Sqlite('user_groups.db').get_id_listings('groups') if int(a) == int(_user)]
        return cls(_groups)

    @classmethod
    def display_group(cls, _user:int, _id:int) -> typing.Any:
        [_groups] = [b for a, b in tigerSqlite.Sqlite('user_groups.db').get_id_listings('groups') if int(a) == int(_user)]
        return {'status':'false'} if int(_id)-1 >= len(_groups) else _group(int(_id), _groups[int(_id)-1])

    @classmethod
    def create_group(cls, _user:int, _payload:dict) -> None:
        [_groups] = [b for a, b in tigerSqlite.Sqlite('user_groups.db').get_id_listings('groups') if int(a) == int(_user)]
        _d = datetime.datetime.now()
        print(_payload)
        _new_groups = _groups+[{**_payload, 'timestamp':'-'.join(str(getattr(_d, i)) for i in ['year', 'month', 'day'])}]
        tigerSqlite.Sqlite('user_groups.db').update('groups', [('listings', _new_groups)], [('id', _user)])
        return str(len(_new_groups))
