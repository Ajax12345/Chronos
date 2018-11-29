import tigerSqlite, typing, random
import sqlite3, chronos_utilities, re

class _searchUsers:
    def __init__(self, _results:list) -> None:
        self.results = _results
    @classmethod
    def search_users(cls, _query:str, avoid:list=[]) -> typing.Callable:
        return cls([i for i in Users.all_users() if _query.lower() in i.name.lower() and i.id not in avoid])
    def __bool__(self):
        return bool(self.results)
    def __iter__(self):
        yield from self.results

class Users:
    headers = ['id', 'name', 'email', 'password', 'settings']
    avatar_colors = ['#3446FB', '#EA2323', '#C9C9C9', '#FFAB03', '#FFE003', '#03FF1E', '#14D229', '#14D2A1', '#D462FF', '#FE00C8', '#FE0060', '#00FEE3']
    @classmethod
    def get_user_initials(cls, _name:str) -> str:
        return _name[0] if not re.findall('\s+', _name) else ''.join(a for a, *_ in _name.split())
    @classmethod
    def update_profile(cls, _id:int, **kwargs:typing.Dict[str, str]) -> None:
        tigerSqlite.Sqlite('user_credentials.db').update('credentials', [('name', kwargs['name']), ('email', kwargs['email'])], [('id', int(_id))])
        return re.sub('\s+', '', kwargs['name']), cls.get_user_initials(kwargs['name'])

    @classmethod
    def _rand_avatar_color(cls) -> str:
       return random.choice(cls.avatar_colors) 
    @classmethod
    def validate_user_registration(cls, _name:str, _email:str) -> dict:
        if any(c == _name for c, _ in tigerSqlite.Sqlite('user_credentials.db').get_name_email('credentials')):
            return {'success':'False', 'for':'name'}
        if any(b == _email for _, b in tigerSqlite.Sqlite('user_credentials.db').get_name_email('credentials')):
            return {'success':'False', 'for':'email'}
        return {'success':'True'}
    @classmethod
    def max_user_id(cls):
        _ids = [a for [a] in sqlite3.connect('user_credentials.db').cursor().execute("SELECT id FROM credentials")]
        return 0 if not _ids else max(_ids)
    @classmethod
    def register_user(cls, *args:list) -> dict:
        _name, _email, _password = args
        _check = cls.validate_user_registration(_name, _email)
        if _check['success'] == 'True':
            tigerSqlite.Sqlite('user_credentials.db').insert('credentials', ('id', cls.max_user_id()+1), ('name', _name), ('email', _email), ('password', _password), ('settings', {'hide_email':False, 'avatar_color':cls._rand_avatar_color()}))
        return _check, cls.get_user(email=_email, password=_password)

    @classmethod
    def validate_credentials(cls, _email:str, _password:str) -> dict:
        return {'success':'False', 'for':'password'} if not any(a == _email and b == _password for a, b in tigerSqlite.Sqlite('user_credentials.db').get_email_password('credentials')) else {'success':'True'}
   
    @classmethod
    def all_users(cls) -> list:
        return list(map(cls, tigerSqlite.Sqlite('user_credentials.db').get_id_name_email_password_settings('credentials')))
        

    @classmethod
    @chronos_utilities.validate_parameters
    def get_user(cls, **_kwargs:dict) -> typing.Callable:
        
        return cls([i for i in tigerSqlite.Sqlite('user_credentials.db').get_id_name_email_password_settings('credentials') if (lambda x:all(x[c] == _kwargs[c] for c in _kwargs))(dict(zip(cls.headers, i)))][0])

    @classmethod
    def login_user(cls, _email:str, _password:str) -> typing.Tuple[dict, typing.Callable]:
        _check = cls.validate_credentials(_email, _password)
        return _check, None if _check['success'] == 'False' else cls.get_user(email=_email, password = _password)

    def __init__(self, _row:typing.List[typing.Any]) -> None:
        self.__dict__ = dict(zip(self.__class__.headers, _row))
        self.id = int(self.id)
    @property
    def hide_email(self):
        return self.settings['hide_email']
    @property
    def condensed_name(self):
        return re.sub('\s+', '', self.name)
    @property
    def initials(self):
        return self.__class__.get_user_initials(self.name)
    @property
    def avatar_color(self):
        return self.settings['avatar_color']
    def __repr__(self):
        return f'User(id={self.id}, name={self.name})'