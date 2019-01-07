import typing, re, itertools
import tigerSqlite, chronos_users, user_groups
import datetime, calendar, json


class _last_updated:
    def __init__(self, *args) -> None:
        print('args here', args)
        [self._user, self._datetime], _timestamp = args
    @property
    def user(self):
        return chronos_users.Users.get_user(id=self._user)
    @property
    def last_updated(self):
        _result = datetime.datetime.now() - self._datetime
        _new_result = [[i, getattr(_result, i, None)] for i in ['years', 'months', 'days', 'minutes', 'seconds'] if getattr(_result, i, None)]
        return 'Updated just now' if not _new_result else f'Last updated {_new_result[0][-1]} {_new_result[0][0]}{"s" if _new_result[0][-1] != 1 else ""}'
    
    @classmethod
    def max_timestamps(cls, _timelistings, _timestamp) -> typing.Callable:
        return  cls(min([[a, datetime.datetime(*(lambda x:[x[-1], x[0], x[1]])(list(map(int, _timestamp.split('-')))), *b['timerange'][0])] for a, b in _timelistings], key=lambda x:x[-1]), _timestamp)

    @property
    def full_message(self):
        return f'Last updated by <a href="/user/{self.user.id}" style="color:black"><strong>@{self.user.condensed_name}</strong></a>'
        


class _menu_event:
    def __init__(self, _logged_in:int, _payload:dict, _timestamp) -> None:
        self.logged_in = _logged_in
        self.default_timestamp = _timestamp
        self.__dict__.update(_payload)


    @property
    def button_text(self):
        _user_obj = [i for i in self.user_data if i['user'] == self.logged_in]
        if not _user_obj:
            return 'Add availability'
        _user_obj = _user_obj[0]
        return 'Add availability' if _user_obj['available'] != 'True' else ['View availability', 'Add availability'][not bool(_user_obj['timeslots'])]


    @property
    def lasted_updated_by(self):
        _timeslots = [[i['user'], c] for i in self.user_data for c in i['timeslots']]
        print('timeslots display below')
        print(_timeslots)
        if not _timeslots:
            class __message:
                full_message = 'Be the first to add your availability'
            return __message
        return _last_updated.max_timestamps(_timeslots, self.default_timestamp)
        
    @property
    def date_title(self):
        _m, _d, _y = map(int, re.findall('\d+', self.date))
        _today = datetime.datetime.now()
        if datetime.date(_y, _m, _d) == datetime.date(*[getattr(_today, i) for i in ['year', 'month', 'day']]):
            return "Today"
        if datetime.date(_y, _m, _d) == datetime.date(*[getattr(_today, i) for i in ['year', 'month', 'day']]) + datetime.timedelta(1):
            return 'Tomorrow'
        _calendar = list(calendar.Calendar().monthdatescalendar(_y, _m))
        _week = [i for i in _calendar if any(c == datetime.date(_y, _m, _d) for c in i)][0]
        _day = Event.days[[i for i, a in enumerate(_week) if a == datetime.date(_y, _m, _d)][0]]
        return f'{_day}, {Event.months[_m-1]} {_d}, {_y}'




class _tag_obj:
    def __init__(self, _name:str, _color:str) -> None:
        self.name, self.color = _name, _color

class _added_user:
    def __init__(self, _user:int, _tags:typing.List[_tag_obj], _row_id = 0, _end=1) -> None:
        self.user, self.tags = chronos_users.Users.get_user(id=_user), _tags
        self.row_id, self.end_val = _row_id, _end
    @property
    def row_class(self):
        return 'round_both' if self.end_val == 1 else 'widget_top' if not self.row_id else 'widget_bottom' if self.row_id == self.end_val-1 else 'is_logged_in'

class _message_obj:
    def __init__(self, _creator:int, _payload:dict) -> None:
        self.__dict__ =  {'creator':_creator, **_payload}
    @property
    def is_by_created(self):
        return self.creater == self.poster 
    @property
    def poster_obj(self):
        return chronos_users.Users.get_user(id=self.poster)
    @property
    def timestamp(self):
        _posted = datetime.datetime(*self.posted_on)
        _d = datetime.datetime.now()
        if datetime.date(*[getattr(_posted, i) for i in ['year', 'month', 'day']]) == datetime.date(*[getattr(_d, i) for i in ['year', 'month', 'day']]):
            _preced = "Today"
        elif all(getattr(_posted, i) == getattr(_d, i) for i in ['year', 'month']) and _d.day - 1 == _posted.day:
            _preced = 'Yesterday'
        else:
            _preced = f'{Event.months[_posted.month-1]} {_posted.day}, {_posted.year}'
        return f'{_preced} at {12 if _posted.hour == 24 else _posted.hour%12 if _posted.hour > 12 else _posted.hour}:{"" if _posted.minute > 9 else "0"}{_posted.minute} {"PM" if _posted.hour > 12 else "AM"}'



class _spacer:
    def __init__(self, _count:int, width:int=120) -> None:
        self.count, self.role = _count, 'spacer'
        self.width = width
    @property
    def is_spacer(self):
        return self == "spacer"
    def __eq__(self, _val:str) -> bool:
        return 'spacer' == _val

class _timeslot:
    def __init__(self, _count:int, _payload:dict) -> None:
        self.__dict__ = {'count':_count, 'role':'timeslot', **_payload}
    
    @property
    def popover_text(self):
        return {1:'This is an optimal timerange for me', 2:'I am available but would rather not meet now', 3:'I am available only if absolutely necessary'}[int(self.preference)]

    @property
    def is_spacer(self):
        return self == 'spacer'
    def __eq__(self, _val:str) -> bool:
        return _val == 'timeslot'
    @property
    def timeslot_class(self):
        return {1:'first_choice', 2:'second_choice', 3:'third_choice'}[int(self.preference)]


class _timeslot_row:
    def __init__(self, _payload:dict, **kwargs:dict) -> None:
        self.__dict__ = {**_payload, **kwargs}
        print('in _timeslot_row init')
        print(self.__dict__)
    @property
    def obj_class(self):
        return 'time_hour_block' if self.logged_in == self.user else '_time_hour_block'
    
    @property
    def is_available(self):
        return self.available == 'True'

    @property
    def user_obj(self):
        return chronos_users.Users.get_user(id=self.user)

    @property
    def error_bars(self):
        yield from range(48)
    
    @property
    def is_creator(self):
        return self.logged_in == self.user
    def __iter__(self):
        if self.available != 'True':
            raise ValueError(f"User is not available on {self.timestamp}")
        _count, _start = itertools.count(1), 0    
        for _slot in sorted(self.timeslots, key=lambda x:x['timerange']):
            [hour1, minute1], [hour2, minute2] = _slot['timerange']
            for _ in range(_start, hour1-1):
                yield _spacer(next(_count))
                _start += 1
            _t = _timeslot(next(_count), _slot)
            print(_slot['timerange'])
            _factor = (hour2 if not minute2 else hour2+1) - hour1
            _t.main_width = _factor*120
            _start += _factor
            print(_start)
            _t.width = ((120*hour2)+round((minute2/float(60))*120))-((120*hour1)+round((minute1/float(60))*120))-3
            _t.offset = round((minute1/float(60))*120)
            yield _t
        print('start before trailing', _start)
        for _ in range(_start, 24):
            print('in trailing')
            yield _spacer(next(_count))
    @classmethod
    def test_feature(cls) -> None:
        _d = d = {'user': 1, 'timeslots': [], 'lasted_added': [], 'available': 'True'}
        for i in cls(_d):
            print(i.role)
            if not i.is_spacer:
                print([getattr(i, c) for c in ['main_width', 'width', 'offset']])

        
            
class Event:
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    def __init__(self, _logged_in:int, _id:int, _payload:dict, _timestamp:str=None) -> None:
        self.logged_in = _logged_in
        self.event_id = _id
        self.default_timestamp = _timestamp 
        self.__dict__.update(_payload)
        self.default_timestamp = _timestamp if _timestamp is not None else self.days[0]['date']
        print('default timestamp here', self.default_timestamp)
    @property
    def can_view_event(self):
        return self.visibility == 'public' or self.logged_in in self.all_users


    @property
    def next_timestamp(self):
        [_result] = [i for i, a in enumerate(self.days) if a['date'] == self.default_timestamp]
        return None if _result == len(self.days)-1 else self.days[_result+1]['date']
    @property
    def previous_timestamp(self):
        [_result] = [i for i, a in enumerate(self.days) if a['date'] == self.default_timestamp]
        return None if not _result else self.days[_result-1]['date']
    @property
    def has_next(self):
        return self.next_timestamp is not None

    @property
    def current_timestamp_header(self):
        _m, _d, _y = map(int, re.findall('\d+', self.default_timestamp))
        return f'{Event.months[_m-1]} {_d}, {_y}'
    @property
    def can_add_availability(self):
        return not self.logged_in in self.all_users
    
    def basic_tags(self, _id:int) -> typing.List[_tag_obj]:
        return [_tag_obj('you' if _id == self.logged_in else 'owner', '#FABC09')] if self.logged_in == _id or _id == self.creator else []

    @property
    def all_timeslots(self):
        [_full_day] = [i for i in self.days if i['date'] == self.default_timestamp]
        _day_dict = {i['user']:i for i in _full_day['user_data']}
        return [_timeslot_row(_day_dict[i],  logged_in = self.logged_in, timestamp=self.default_timestamp) for i in self.all_users]

    @property
    def user_roster(self):
        return [_added_user(a, self.basic_tags(a), _row_id=i, _end=len(self.all_users)) for i, a in enumerate(self.all_users)]

    @property
    def has_previous(self):
        return self.previous_timestamp is not None

    def __getattr__(self, _name:str) -> typing.Any:
        return self.basic[_name]
    @property
    def created_on(self):
        _y, _m, _d = self.basic['created_on']
        return f'{Event.months[int(_m)-1]} {_d}, {_y}'
    @property
    def has_description(self):
        return bool(self.description)

    @property
    def has_messages(self):
        return bool(self.messages)

    @property
    def has_location(self):
        return bool(self.location)
    def __iter__(self):
        _sorted_result = sorted(self.days, key=lambda x:datetime.date(*(lambda c:[c[-1], c[0], c[1]])(list(map(int, re.findall('\d+', x['date']))))))
        for i in _sorted_result:
            yield _menu_event(self.logged_in, i, self.default_timestamp)
    @property
    def message_num(self):
        return len(self.messages)

    @property
    def all_messages(self):
        return [_message_obj(self.basic['creator'], i) for i in self.messages]

    @property
    def avatar_display(self):
        return [chronos_users.Users.get_user(id=i) for i in self.all_users[:3]]

    @property
    def trailing_message(self):
        return f'{len(self.all_users[3:])} other{"s" if len(self.all_users[3:]) != 1 else ""}. '

    @property
    def logged_in_is_creator(self):
        return self.creator == self.logged_in

    def is_creator(self, _id:int) -> typing.Any:
        return ['owner', 'red'] if _id == self.creator else False

    def is_you(self, _id:int) -> typing.Any:
        return ['you', '#37176A'] if self.logged_in == _id else False

    def all_tags(self, _user:int) -> typing.List[_tag_obj]:
        return [_tag_obj(*i) for i in [self.is_creator(_user), self.is_you(_user)] if i]

    @property
    def see_all_list(self):
        return [_added_user(i, self.all_tags(i)) for i in self.all_users]

    @property
    def has_trailing_users(self):
        return len(self.all_users) > 3
        
    @property
    def creator_obj(self):
        return chronos_users.Users.get_user(id=self.creator)



class Events:
    """
    filename: user_events.db
    tablename: events
    columns: id real, listing text
    """
    @staticmethod
    def create_event_payload(_creator_id:int, _id:int, _payload:dict) -> dict:
        print(_payload)
        _basic, _dates, _people, _groups, _visibility = _payload
        _d = datetime.datetime.now()
        _all_users = list(set([*_people, *[i for b in _groups for i in user_groups.all_users_in_group(_id, b)], _creator_id]))
        return {'id':_id, 'basic':{**_basic, 'creator':_creator_id, 'visibility':['private', 'public'][_visibility], 'created_on':[getattr(_d, i) for i in ['year', 'month', 'day']]}, 'status':1, 'avoid_users':[], 'groups':_groups, 'people':[*_people, _creator_id], 'all_users':_all_users, 'days':[{"date":i, 'user_data':[{'user':c, 'timeslots':[], 'lasted_added':[], 'available':'True'} for c in _all_users]} for i in _dates], 'messages':[], 'finalized':[]}

    @classmethod
    def create_event(cls, _user:int, _payload:dict, _flag:bool = False) -> typing.Any:
        [_listing] = [b for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if int(a) == int(_user)]
        _all_events = [c['id'] for _, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') for c in b]
        _max_num = 0 if not _all_events else max(_all_events)
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', _listing+[cls.create_event_payload(_user, _max_num+1, _payload)])], [('id', _user)])
        return _max_num + 1

    @classmethod
    def post_message(cls, _poster:int, _payload:dict) -> Event:
        [[_owner, _current_events]] = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(c['id']) == int(_payload['id']) for c in b)]
        _d = datetime.datetime.now()
        new_event = [{**i, 'messages':i['messages']+[{'message':_payload['message'], 'poster':_poster, 'posted_on':[getattr(_d, c) for c in ['year', 'month', 'day', 'hour', 'minute','second']]}]} if int(i['id']) == int(_payload['id']) else i for i in _current_events]
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', new_event)], [('id', _owner)])
        return cls.get_event(int(_payload['id']), _poster)

    @classmethod
    def get_event(self, _id:int, _logged_in:int, _set_timestamp:str=None) -> Event:
        [_event] = [i for _, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') for i in b if int(i['id']) == int(_id)]
        return Event(_logged_in, _id, _event, _set_timestamp)

    @classmethod
    def event_exists(cls, _id:int) -> bool:
        _events = [b for _,b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events')]
        return any(int(i['id']) == int(_id) for c in _events for i in c)

    @classmethod
    def add_user_availability(cls, _user:int, _payload:dict) -> Event:
        _owner, _event_data = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(c['id']) == int(_payload['id']) for c in b)][0]
        [_event] = [c for c in _event_data if int(c['id']) == int(_payload['id'])]
        _new_payload = {**_event, 'people':_event['people']+([] if _user in _event['people'] else [_user]), 'all_users':_event['all_users']+([] if _user in _event['all_users'] else [_user]), 'days':[{**h, 'user_data':[*h['user_data'], {'user': _user, 'timeslots': [], 'lasted_added': [], 'available': 'True'}]} for h in _event['days']]}
        new_listing = [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _event_data]
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', new_listing)], [('id', _owner)])
        return cls.get_event(int(_payload['id']), _user, _set_timestamp=_payload['timestamp'])

    @classmethod
    def add_timeslot(cls, _poster:int, _payload:dict) -> typing.Callable:
        print('got payload here for update', _payload)
        _hour1, _minutes1, meridian1, _hour2, _minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|(?<=\d\s)[AMP]+', _payload['timerange'])
        hour1, hour2 = int(_hour1) + (0 if meridian1 == 'AM' else 12), int(_hour2) + (0 if meridian2 == 'AM' else 12) 
        minutes1, minutes2 = int(_minutes1), int(_minutes2)
        _d = datetime.datetime.now()
        posted_date = [getattr(_d, i) for i in ['year', 'month', 'day', 'hour', 'minute', 'second']]
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _current_event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_current_event, 'days':[i if i['date'] != _payload['timestamp'] else {**i, 'user_data':[c if int(c['user']) != int(_poster) else {**c, 'timeslots':[*c['timeslots'], {'timerange':[[hour1, minutes1], [hour2, minutes2]], 'message':_payload['message'], 'preference':_payload['preference']}], 'lasted_added':[*c['lasted_added'], {'user':_poster, 'timestamp':posted_date}]} for c in i['user_data']]} for i in _current_event['days']]}
        print(json.dumps(_new_payload, indent=4))
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        return cls.get_event(int(_payload['id']), _poster, _set_timestamp=_payload['timestamp'])

    @classmethod
    def mark_unavailable(cls, _poster:int, _payload:dict) -> Event:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _current_event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_current_event, 'days':[i if i['date'] != _payload['timestamp'] else {**i, 'user_data':[c if int(c['user']) != int(_poster) else {**c, 'available':'False'} for c in i['user_data']]} for i in _current_event['days']]}
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        print(json.dumps(_new_payload, indent=4))
        return cls.get_event(int(_payload['id']), _poster, _set_timestamp=_payload['timestamp'])
    
    @classmethod
    def mark_available(cls, _poster:int, _payload:dict) -> Event:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _current_event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_current_event, 'days':[i if i['date'] != _payload['timestamp'] else {**i, 'user_data':[c if int(c['user']) != int(_poster) else {**c, 'available':'True'} for c in i['user_data']]} for i in _current_event['days']]}
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        print(json.dumps(_new_payload, indent=4))
        return cls.get_event(int(_payload['id']), _poster, _set_timestamp=_payload['timestamp'])

    @classmethod
    def remove_timeslot(cls, _poster:int, _payload:dict) -> None:
        _hour1, _minutes1, meridian1, _hour2, _minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|(?<=\d\s)[AMP]+', _payload['timerange'])
        hour1, hour2 = int(_hour1) + (0 if meridian1 == 'AM' else 12), int(_hour2) + (0 if meridian2 == 'AM' else 12) 
        minutes1, minutes2 = int(_minutes1), int(_minutes2)
        _timerange = [[hour1, minutes1], [hour2, minutes2]]
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _current_event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_current_event, 'days':[i if i['date'] != _payload['timestamp'] else {**i, 'user_data':[c if int(c['user']) != int(_poster) else {**c, 'timeslots':[h for h in c['timeslots'] if h['timerange'] != _timerange]} for c in i['user_data']]} for i in _current_event['days']]}
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        return cls.get_event(int(_payload['id']), _poster, _set_timestamp=_payload['timestamp'])


class About:
    def __init__(self, _user:int, _event:int, _date:str, _day_data:dict) -> None:
        self.user, self.event_id, self.day_data= chronos_users.Users.get_user(id=_user), _event, _day_data
        self.timestamp = _date

    @property
    def is_available(self):
        return self.day_data['available'] == 'True'

    @property
    def button_message(self):
        return 'Add availability' if self.day_data["available"] != 'True' else 'I am not available today'
    
    @property
    def full_timestamp(self):
        _m, _d, _y = map(int, re.findall('\d+', self.timestamp))
        return f'{Event.months[_m-1]} {_d}, {_y}'

    @property
    def button_flag(self):
        return '1' if self.day_data["available"] != 'True' else '0'
    
    @property
    def button_color(self):
        return '#EA2B43' if not int(self.button_flag) else '#21DCAC'

    
    @property
    def timestamp_message(self):
        return '<i>You have not added any timeslots</i>' if not self.day_data['timeslots'] else f'You have added <span style="color:#FABC09">{len(self.day_data["timeslots"])}</span> timeslot{"s" if len(self.day_data["timeslots"]) != 1 else ""}'

    @classmethod
    def get_about_current(cls, _payload:dict) -> typing.Callable:
        _event = Events.get_event(int(_payload['event_id']), int(_payload['user_id']))
        return cls(int(_payload['user_id']), int(_payload['event_id']), _payload['timestamp'], (lambda x:[c for c in x['user_data'] if c['user'] == int(_payload['user_id'])][0])([i for i in _event.days if i['date'] == _payload['timestamp']][0]))
