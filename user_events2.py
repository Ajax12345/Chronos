import typing, re, itertools
import tigerSqlite, chronos_users, user_groups
import datetime, calendar, json
import user_calendar, functools, chronos_utilities


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
        print('failed timelistings here', _timelistings)
    
        return cls(sorted([[a['user'], datetime.datetime(*a['timestamp'])] for a in _timelistings], key=lambda x:x[-1])[-1], _timestamp)

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
        _timeslots = [i for b in self.user_data for i in b['lasted_added']]
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


class _event_role:
    @property
    def is_spacer(self):
        return self.role == 'spacer'
    @property
    def is_timeslot(self):
        return self.role == 'timeslot'
    @property
    def is_previous_event(self):
        return self.role == 'previous_event'

class _spacer(_event_role):
    def __init__(self, _count:int, width:int=120) -> None:
        self.count, self.role = _count, 'spacer'
        self.width = width

    def __eq__(self, _val:str) -> bool:
        return 'spacer' == _val

class _timeslot(_event_role):
    def __init__(self, _count:int, _payload:dict) -> None:
        self.__dict__ = {'count':_count, 'role':'timeslot', **_payload}
    
    @property
    def popover_text(self):
        return {1:'This is an optimal timerange for me', 2:'I am available but would rather not meet now', 3:'I am available only if absolutely necessary'}[int(self.preference)]

    @property
    def timeslot_class(self):
        return {1:'first_choice', 2:'second_choice', 3:'third_choice'}[int(self.preference)]

class _calendar_event(_event_role):
    def __init__(self, _count:int, _user:int, _payload:dict) -> None:
        self.user = _user
        self.role = 'previous_event'
        self.__dict__.update(_payload)
        self.count = _count

    def __getattr__(self, _val:str) -> typing.Any:
        return getattr(self.obj, _val)

    @property
    def condensed_title(self):
        return self.title[:8]+'...' if len(self.title) > 8 else self.title  



class _timeslot_row:
    def __init__(self, _payload:dict, **kwargs:dict) -> None:
        self.__dict__ = {**_payload, **kwargs}
        print('in _timeslot_row init')
        print(self.__dict__)
    @property
    def obj_class(self):
        return 'time_hour_block' if self.logged_in == self.user else 'time_hour_block'
    
    @property
    def can_add_timeslots(self):
        return 'True' if self.logged_in == self.user else 'False'

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

    def calc_timerange(self, _timerange:str) -> typing.List:
        _hour1, _minutes1, _meridian1, _hour2, _minutes2, _meridian2 = re.findall('\d+|[AMP]+', _timerange)
        return [[int(_hour1)+(0 if _meridian1 == 'AM' else 12), int(_minutes1)], [int(_hour2)+(0 if _meridian2 == 'AM' else 12), int(_minutes2)]]

    @property
    def user_calendar_events(self):
        _m, _d, _y = map(int, re.findall('\d+', self.timestamp))
        c = user_calendar.Calendar.events_by_day(self.logged_in, datetime.date(_y, _m, _d))
        return [{'timerange':self.calc_timerange(i.timerange), 'obj':i} for i in c]
    
    def __iter__(self):
        if self.available != 'True':
            raise ValueError(f"User is not available on {self.timestamp}")
        _count, _start = itertools.count(1), 0    
        for _slot in sorted(self.timeslots+(self.user_calendar_events if self.is_creator else []), key=lambda x:x['timerange']):
            [hour1, minute1], [hour2, minute2] = _slot['timerange']
            for _ in range(_start, hour1-1):
                yield _spacer(next(_count))
                _start += 1
            _current_count = next(_count)
            _t = _timeslot(_current_count, _slot) if 'obj' not in _slot else _calendar_event(_current_count, self.logged_in, {'obj':_slot['obj']})
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


class overlap_parent:
    def __getattr__(self, _val:str) -> bool:
        return self.role == _val[3:]    

class _option_timeslots(overlap_parent):
    def __init__(self, _data:typing.List[dict]) -> None:
        self.data = _data
        print('data in option_timeslot', self.data)
    def __contains__(self, _user:int) -> bool:
        return any(i['user'] == _user for i in self.data)
    @property
    def opacity(self):
        _scale = {1:3, 2:2, 3:1}
        return sum(_scale[i['preference']] for i in self.data)/float(len(self.data)*3)  
    def __repr__(self):
        return f'Overlap(users={len(self.data)})'
    def __bool__(self):
        return bool(self.data)
    @property
    def role(self):
        return 'overlap_timeslot'

class _no_overlap_found(overlap_parent):
    def __init__(self, _ind:int) -> None:
        self.role, self.ind = 'no_overlap', _ind
    
class _overlap_spacer(overlap_parent):
    def __init__(self, _ind:int) -> None:
        self.role, self.ind = 'spacer', _ind


class _finalized_day:
    def __init__(self, _logged_in:int, _payload:dict, _all_users:typing.List[int], _iter:int, _day_len:int) -> None:
        self.__dict__ = {"logged_in":_logged_in, **_payload, 'all_users':_all_users, 'ind':_iter, 'day_len':_day_len}
    @property
    def timestamp(self):
        _m, _d, _y = map(int, re.findall('\d+', self.date))
        return f'{Event.months[_m-1]} {_d}, {_y}'

    @property
    def day_class(self):
        #return 'widget_top' if not self.ind else 'widget_bottom' if self.ind == self.day_len-1 else 'round_both' if 
        return 'round_both' if self.day_len == 1 else 'widget_top' if not self.ind else 'widget_bottom' if self.ind == self.day_len-1 else 'is_logged_in'

    @property
    def filtered_listings(self):
        return [i for i in self.user_data if i["timeslots"]]
    
    @property
    def missing_users(self):
        return len(self.user_data) - len(self.filtered_listings)

    @staticmethod
    def _can_call(_stamp:typing.List, _val:int) -> bool:
        return True if len(_stamp) < 2 else _val >= _stamp[[1, 0][len(_stamp) == 2]]

    @classmethod
    def timestamp_combos(cls, d, _current=[]):
        if len(_current) == 4:
            yield _current
        else:
            for i in d[0]:
                if cls._can_call(_current, i):
                    yield from cls.timestamp_combos(d[1:], _current+[i])
    

    def is_overlap(self, _a:datetime.datetime, _b:datetime.datetime, stamp:functools.partial, _payload:dict) -> bool:
        [h1, m1], [h2, m2] = _payload['timerange']
        _d1, _d2 = stamp(h1-1 if h1 == 24 else h1, 59 if h1 == 24 else m1), stamp(h2-1 if h2 == 24 else h2, m2 if h2 != 24 else 59)
        return _a >= _d1 and _b <= _d2


    @staticmethod
    def max_timestamp_key(_vals:list) -> int:
        [a, b], _ = _vals
        return (b.hour*60+b.minute)-(a.hour*60+a.minute)

    def _overlap(self) -> typing.Any:
        _filtered = self.filtered_listings
        _m, _d, _y = map(int, re.findall('\d+', self.date))
        _stamp = functools.partial(datetime.datetime, _y, _m, _d)
        _groupings = [[_stamp(a, b), _stamp(*c)] for a, b, *c in self.__class__.timestamp_combos([range(1, 24), range(0, 60), range(1, 24), range(0, 60)])]
        _flattened_timeslots = [{'user':b['user'], **i} for b in self.user_data for i in b['timeslots']]
        _final_time_ranges = [[[a, b], _option_timeslots([i for i in _flattened_timeslots if self.is_overlap(a, b, _stamp, i)])] for a, b in _groupings]
        _new_ranges = [[a, b] for a, b in _final_time_ranges if all(c in b for c in self.all_users)]
        return _new_ranges if not _new_ranges else max(_new_ranges, key=self.__class__.max_timestamp_key)

    @staticmethod
    def not_overlap(_a:typing.List[datetime.datetime], _b:typing.List[datetime.datetime]) -> bool:
        return _a[-1] <= _b[0]

    def overlap(self) -> list:
        print('in overlap calc method')
        _m, _d, _y = map(int, re.findall('\d+', self.date))
        _stamp = functools.partial(datetime.datetime, _y, _m, _d)
        _flattened_timeslots = [{'user':b['user'], **i} for b in self.user_data for i in b['timeslots'] if b['timeslots'] and b['available'] == 'True']
        print('flattened_timeslots', _flattened_timeslots)
        #_start, _end = zip(*[[a, b] for a, b in map(lambda x:x['timerange'], _flattened_timeslots)])
        t = list(zip(*[[a, b] for a, b in map(lambda x:x['timerange'], _flattened_timeslots)]))
        print('got t here', t)
        if not t:
            return t
        _start, _end = t
        _start, _end = [[a-1 if a == 24 else a, 59 if a == 24 else b] for a, b in _start],[[a-1 if a == 24 else a, 59 if a == 24 else b] for a, b in _end] 
        print(_start, _end)
        groupings = [[_stamp(*a), _stamp(*b)] for a in _start for b in _end]
        new_groups = [[[a, b], _option_timeslots([i for i in _flattened_timeslots if self.is_overlap(a, b, _stamp, i)])] for a, b in groupings]
        _new_ranges = sorted([[[h, k], b] for [h, k], b in new_groups if all(c['user'] in b for c in _flattened_timeslots) and h <= k], key=lambda x:x[0])
        _new_ranges = [a for i, a in enumerate(_new_ranges) if all(a[0] != c[0] for c in _new_ranges[:i])]
        '''
        print('plain old new_groups', new_groups)
        class _groupby_wrapper:
            def __init__(self, _obj) -> None:
                self._obj = _obj
            def __eq__(self, _obj1) -> bool:
                return _finalized_day.not_overlap(self._obj[0], _obj1._obj[0])

        _new_ranges = sorted([[[h, k], b] for [h, k], b in new_groups if all(c['user'] in b for c in _flattened_timeslots) and h <= k], key=lambda x:x[0])
        print('new sorted ranges here', _new_ranges)
        _new_ranges = [a for i, a in enumerate(_new_ranges) if all(a[0] != c[0] for c in _new_ranges[:i])]
        _new_vals = [[h._obj for h in b] for _, b in itertools.groupby(list(map(_groupby_wrapper, _new_ranges)))]
        print('this is the newval listing here', _new_vals)
        return [max(i, key=self.__class__.max_timestamp_key) for i in _new_vals]
        '''
        return [[[a, b], c] for [a, b], c in _new_ranges if 60*(b.hour-a.hour)+(b.minute-a.minute)]

    def __iter__(self):
        _count, _start = itertools.count(1), 0    
        _r = self.overlap()
        print('r in iter method', _r)
        if not _r:
            for _ in range(24):
                yield _no_overlap_found(self.ind)
        else:
            for [a, b], _t in _r:
                for _ in range(_start, a.hour-1):
                    yield _overlap_spacer(next(_count))
                    _start += 1
            
                _factor = (b.hour if not b.minute else b.hour+1) - a.hour
                _t.main_width = _factor*120
                _start += _factor
                _t.timestamp = f'{a.hour if a.hour < 13 else 12 if a.hour == 24 else a.hour%12}:{"" if a.minute > 9 else "0"}{a.minute} {"AM" if a.hour <= 12 else "PM"} - {b.hour if b.hour < 13 else 12 if b.hour == 24 else b.hour%12}:{"" if b.minute > 9 else "0"}{b.minute} {"AM" if b.hour <= 12 else "PM"}'
                _t.width = ((120*b.hour)+round((b.minute/float(60))*120))-((120*a.hour)+round((a.minute/float(60))*120))-3
                _t.offset = round((a.minute/float(60))*120)
                _t.ind = next(_count)
                yield _t
            for _ in range(_start, 24):
                yield _overlap_spacer(next(_count))



    @property
    def is_today(self):
        d = datetime.datetime.now()
        _m, _d, _y = map(int, re.findall('\d+', self.date))
        return datetime.date(_y, _m, _d) == datetime.date(*[getattr(d, i) for i in ['year', 'month', 'day']])

    @property
    def blocks(self):
        yield from range(24)

    @property
    def triangle_class(self):
        return ['triangle_today', 'triangle_other_day'][not self.is_today]

class FinalizedSlot:
    def __init__(self, _logged_in:int, _payload:dict) -> None:
        self.logged_in = _logged_in
        self.__dict__.update(_payload)

    @property
    def is_creator(self):
        #return self.people[0] == self.logged_in
        raise Exception

    @property
    def joined_users(self):
        return ','.join(map(str, self.people))

    @property
    def needs_to_rsvp(self):
        return self.logged_in not in self.people

    
    @property
    def rsvp_text(self):
        return 'Send RSVP' if self.needs_to_rsvp else 'RSVP Sent'
    
    @property
    def rsvp_color(self):
        return ['#21DCAC', '#FABC09'][self.needs_to_rsvp]


    
    @property
    def full_day(self):
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


class StatusBanner:
    def __init__(self, *args:typing.List[str]) -> None:
        self.__dict__ = dict(zip(['text', 'color'], args))

class LastMessage:
    def __init__(self, _data:dict) -> None:
        self.__dict__ = _data
    @property
    def condensed_message(self):
        return self.message if len(self.message) < 30 else self.message[:30]+'...'
    @property
    def poster_obj(self):
        return chronos_users.Users.get_user(id=self.poster)

class Visibility:
    def __init__(self, _status:str) -> None:
        self.status = _status
    @property
    def icon(self):
        return 'fa-users' if self.status == 'public' else 'fa-key'
        
    @property
    def visibility_message(self):
        return f'This event is <strong>{"public" if self.status == "public" else "private"}</strong>'

    @property
    def color(self):
        return ['#FABC09', '#21DCAC'][self.status == 'public']

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
    def has_banner(self):
        return self.status > 1

    @property
    def status_banner(self):
        return StatusBanner(*({1:['not finalized', '#FABC09'], 3:['finalized', '#21DCAC'], 2:['canced', '#FF354D']}[self.status]))

    @property
    def possible_dates(self):
        _dates = [i['date'] for i in getattr(self, 'finalized' if self.finalized else 'days')] 
        return f'{len(_dates)} {"possible " if not self.finalized else ""}date{"s" if len(_dates) != 1 else ""}'
    @property
    def member_message(self):
        return f'{len(self.all_users)} member{"s" if len(self.all_users) != 1 else ""}'
    
    @property
    def has_last_message(self):
        return bool(self.messages)

    @property
    def last_message(self):
        return LastMessage(self.messages[-1])

    @property
    def banner_message(self):
        if not self.has_banner:
            raise AttributeError('class "Event" has no attribute "banner_message"')
        return f'<strong><u>{self.name}</u></strong> has been finalized! See below for more.' if self.status == 3 else f'<strong><u>{self.name}</u></strong> has been canceled'
    
    @property
    def banner_class(self):
        if not self.has_banner:
            raise AttributeError('class "Event" has no attribute "banner_message"')
        return ['event_cancled', 'not_set_scheduled'][self.status == 3]
    
    @property
    def is_finalized(self):
        return bool(self.finalized)

    @staticmethod
    def sorted_datetime_obj(_payload:dict) -> datetime.date:
        _m, _d, _y = map(int, re.findall('\d+', _payload['date']))
        return datetime.date(_y, _m, _d)
    
    @property
    def finalized_day_slots(self):
        return [FinalizedSlot(self.logged_in, i) for i in sorted(self.finalized, key=self.__class__.sorted_datetime_obj)]


    @property
    def visibility_token(self):
        return Visibility(self.visibility)

    @property
    def can_view_event(self):
        return self.visibility == 'public' or self.logged_in in self.all_users

    @property
    def finalized_days(self):
        return [_finalized_day(self.logged_in, a, self.all_users, i, len(self.days)) for i, a in enumerate(self.days)]


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
    def plain_people(self):
        return [chronos_users.Users.get_user(id=i) for i in self.all_users]
    
    @property
    def has_added_people(self):
        return bool(self.people)
    
    @property
    def added_groups(self):
        return [i for i in user_groups.Groups.user_groups(self.logged_in) if i.id in self.groups]

    @property
    def has_added_groups(self):
        return bool(self.groups)

    
    @property
    def created_owned_groups(self):
        return [i for i in user_groups.Groups.user_groups(self.logged_in) if i.id not in self.groups]

    @property
    def has_created_groups(self):
        return bool(self.created_owned_groups)


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


class _status_obj:
    def __init__(self, _flag:str) -> None:
        self.flag = _flag
    @property
    def text(self):
        return 'No response' if self.flag == 'True' else 'Not available'
    @property
    def background_color(self):
        return ['#E9E9E9', '#FC9FAA'][self.flag != 'True']
    @property
    def color(self):
        return ['#767676', '#FF354D'][self.flag != 'True']


class _user_overlap_results:
    class overlap:
        def __init__(self, _payload:dict) -> None:
            self._payload = _payload
        @property
        def user(self):
            return chronos_users.Users.get_user(id=self._payload['user'])
        @property
        def timestamp(self):
            [_hour1, _minutes1], [_hour2, _minutes2] = self._payload['timerange']
            return f'{_hour1 if _hour1 < 13 else 12 if _hour1 == 24 else _hour1%12}:{"" if _minutes1 > 9 else "0"}{_minutes1} {"AM" if _hour1 < 12 else "PM"} - {_hour2 if _hour2 < 13 else 12 if _hour2 == 24 else _hour2%12}:{"" if _minutes2 > 9 else "0"}{_minutes2} {"AM" if _hour2 < 12 else "PM"}'
    
        @property
        def color(self):
            return {1:'#18A66C', 2:'#D69F00', 3:'#FF354D'}[self._payload['preference']]

        @property
        def background_color(self):
            return {1:'#9BECD8', 2:'#FFE28F', 3:'#FC9FAA'}[self._payload['preference']]
        
        @property
        def status(self):
            return _status_obj(self._payload['available'])

    def __init__(self, _listing:typing.List[dict], _date:datetime.date, timerange:str, _full_users:typing.List[dict]) -> None:
        self.listing, self.timerange, self._date = _listing, timerange, _date
        self.full_users = _full_users
        print('in __init__ of _user_overlap_results', self.listing, self.timerange, self._date)
        self.unavailable_users = [i for i in _full_users if not any(c['user'] == i['user'] for c in self.listing)]

    @property
    def datetime(self):
        return f'{Event.months[self._date.month-1]} {self._date.day}, {self._date.year}'

    def __iter__(self):
        yield from map(self.__class__.overlap, self.listing)

    @property
    def has_unavailable_users(self):
        return bool(self.unavailable_users)
    @property
    def all_unavailable_users(self):
        _sorted_users = sorted(self.unavailable_users, key=lambda x:x['user'])
        yield from map(self.__class__.overlap, [a for i, a in enumerate(_sorted_users) if not any(c['user'] == a['user'] for c in _sorted_users[:i])])    

class EventAttendees:
    def __init__(self, _date:str, _users:str) -> None:
        self.date, self._users = _date, str(_users) if isinstance(_users, int) else _users
        self._full_user_list = list(chronos_users.Users.user_listing_display(list(map(int, re.findall('\d+', self._users)))))
    
    @property
    def has_attendees(self):
        return len(self._full_user_list) > 0

    def __iter__(self):
        yield from self._full_user_list
    @property
    def full_date(self):
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

class Events:
    """
    filename: user_events.db
    tablename: events
    columns: id real, listing text
    """
    @staticmethod
    def create_event_payload(_creator_id:int, _id:int, _payload:dict) -> dict:
        print('payload in create event', _payload)
        _basic, _dates, _people, _groups, _visibility = _payload
        _d = datetime.datetime.now()
        print('here, before issue: ', _groups)
        print('id passed here', _id)
        _all_users = list(set([*_people, *[i for b in _groups for i in user_groups.all_users_in_group(_creator_id, b)], _creator_id]))
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
    def _event_sort_key(cls, _event:dict) -> typing.Tuple[int, int]:
        '''
        hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|[APM]+', _event['timerange'])
        return (int(hour1)+(0 if meridian1 == 'AM' else 12)+int(minutes1), int(hour2)+(0 if meridian2 == 'AM' else 12)+int(minutes2))
        '''
        hour1, minutes1, meridian1, hour2, minutes2, meridian2 = re.findall('\d+(?=:)|(?<=:)\d+|[APM]+', _event['timerange'])
        return [(int(hour1)+(0 if meridian1 == 'AM' else 12), int(minutes1)), (int(hour2)+(0 if meridian2 == 'PM' else 12), int(minutes2))]
    
    @classmethod
    def respond_rsvp(cls, _user:int, _payload:dict) -> None:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _current_event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_current_event, 'finalized':[i if i['date'] != _payload['date'] else {**i, 'people':i['people']+[_user]} for i in _current_event['finalized']]}
        _m, _d, _y = re.findall('\d+', _payload['date'])
        print(json.dumps(_new_payload, indent=4))

        for _timerange in _payload['timeranges']:
            _event_creation_payload = {'timestamp':f'{_y}-{_m}-{_d}', 'created_on':str(datetime.datetime.now()), 'title':_new_payload['basic']['name'], 'description':_new_payload['basic']['description'], 'category': 'default', 'background_color': 'rgb(255, 53, 77)', 'border_color': 'rgb(255, 0, 0)', 'month':Event.months[int(_m)-1], 'year':_y, 'timerange':_timerange}
            current_events = [b for a, b in tigerSqlite.Sqlite('user_calendars.db').get_id_events('calendars') if a == _user][-1]
            tigerSqlite.Sqlite('user_calendars.db').update('calendars', [['events', sorted(current_events+[_event_creation_payload ], key=cls._event_sort_key)]], [['id', _user]])
        
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        

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

    @staticmethod
    def is_overlap(start:datetime.datetime, end:datetime.datetime, stamp:functools.partial, _a:list, _b:list) -> bool:
        print('in cls is_overlap', _a, _b)
        a, b = stamp(*[_a[0]-1 if _a[0] == 24 else _a[0], _a[-1] if _a[0] != 24 else 59]), stamp(*[_b[0]-1 if _b[0] == 24 else _b[0], _b[-1] if _b[0] != 24 else 59])
        return a <= start and end <= b


    @classmethod
    def about_overlap(cls, _user:int, _payload:dict) -> typing.Any:
        _e = cls.get_event(int(_payload['id']), int(_user), _set_timestamp = _payload['date'])
        _day = [i for i in _e.days if i['date'] == _payload['date']][0]
        print('day with flag', _day['user_data'])
        _new_grouped = [{'user':a['user'], 'available':a['available'], **i} for a in _day['user_data'] for i in a['timeslots']]
        print('_new_grouped up in here', _new_grouped)
        _m, _d, _y = map(int, re.findall('\d+', _payload['date']))
        _stamp = functools.partial(datetime.datetime, _y, _m, _d)
        _hour1, _minutes1, _meridian1, _hour2, _minutes2, _meridian2 = re.findall('\d+|[AMP]+', _payload['timerange'])
        print('issue presented here', _payload['timerange'])
        hour1, minute1, hour2, minute2 = int(_hour1)+(0 if _meridian1 == 'AM' else 12), int(_minutes1), int(_hour2)+(0 if _meridian2 == 'AM' else 12), int(_minutes2)
        _start, _end = _stamp(hour1 - 1 if hour1 == 24 else hour1, 59 if hour1 == 24 else minute1), _stamp(hour2 - 1 if hour2 == 24 else hour2, 59 if hour2 == 24 else minute2)
        return _user_overlap_results([i for i in _new_grouped if cls.is_overlap(_start, _end, _stamp, *i['timerange'])], datetime.date(_y, _m, _d), _payload['timerange'], _new_grouped+[{'user':i, 'available':'True'} for i in _e.all_users if not any(c['user'] == i for c in _new_grouped)])

    @classmethod
    def event_attendees(cls, _payload:dict) -> None:
        print('got payload in here', _payload)
        return EventAttendees(_payload['date'], _payload['users'])

    @classmethod
    def finalize_event(cls, _poster:int, _payload:dict) -> None:
        print('payload in finalize_event', _payload)
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _grouped_timeslots = [{'date':a, 'timerange':[i['timerange'] for i in b]} for a, b in itertools.groupby(sorted(_payload['day_data'], key=lambda x:x['date']), key=lambda x:x['date'])]
        _new_payload = {**_event, 'status':3, "finalized":[{**i, 'people':[]} for i in _grouped_timeslots]}
        print(json.dumps(_new_payload, indent=4))
        
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        _c = cls.get_event(_payload['id'], _poster)
        return {i:getattr(_c, i) for i in ['name', 'id']}

    @staticmethod
    def update_event_name(_payload:dict) -> None:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_event, 'basic':{**_event['basic'], 'name':_payload['name']}}
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])

    @staticmethod
    def update_event_description(_payload:dict) -> None:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_event, 'basic':{**_event['basic'], 'description':_payload['description']}}
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])

    @staticmethod
    def update_event_location(_payload:dict) -> None:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_event, 'basic':{**_event['basic'], 'location':_payload['location']}}
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])

    @classmethod
    def update_all_users(cls, _user:int, _payload:dict) -> Event:
        print('got stuff here')
        print(_payload)
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_event, 'people':[*_event['people'], *map(int, _payload['people'])], 'all_users':[*_event['all_users'], *map(int, _payload['people'])], 'days':[{**i, 'user_data':[*i['user_data'], *[{'user':int(c), 'timeslots':[], 'lasted_added':[], 'available':'True'} for c in _payload['people']]]} for i in _event['days']]}
        #print(json.dumps(_new_payload, indent=4))
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        return cls.get_event(int(_payload['id']), _user)

    @classmethod
    def remove_user_from_all_users(cls, _user:dict, _payload:dict) -> Event:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_payload = {**_event, 'people':[i for i in _event['people'] if i != int(_payload['user'])], 'all_users':[i for i in _event['all_users'] if i != int(_payload['user'])], 'days':[{**i, 'user_data':[h for h in i['user_data'] if int(h['user']) != int(_payload['user'])]} for i in _event['days']]}
        #print(json.dumps(_new_payload, indent=4))
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        return cls.get_event(int(_payload['id']), _user)


    @classmethod
    def add_groups_to_event(cls, _user:int, _payload:dict) -> Event:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _new_users = [int(i) for b in _payload['groups'] for i in user_groups.all_users_in_group(_user, b) if int(i) not in _event['all_users']]
        _new_payload = {**_event, 'groups':[*_event['groups'], *_payload['groups']], 'all_users':[*_event['all_users'], *_new_users], 'days':[{**i, 'user_data':[*i['user_data'], *[{'user':int(c), 'timeslots':[], 'lasted_added':[], 'available':'True'} for c in _new_users]]} for i in _event['days']]}
        print(json.dumps(_new_payload, indent=4))
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        return cls.get_event(int(_payload['id']), _user)


    @classmethod
    def remove_group_from_event(cls, _user:int, _payload:dict) -> Event:
        _owner, _listing = [[a, b] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') if any(int(i['id']) == int(_payload['id']) for i in b)][0]
        _event = [i for i in _listing if int(i['id']) == int(_payload['id'])][0]
        _group_users = list(user_groups.all_users_in_group(_user, _payload['group']))
        _new_payload = {**_event, 'groups':[i for i in _event['groups'] if int(i) != int(_payload['group'])], 'all_users':[i for i in _event['all_users'] if i not in _group_users], 'days':[{**i, 'user_data':[h for h in i['user_data'] if int(h['user']) not in _group_users]} for i in _event['days']]}
        print('just removed groups from event: ')
        print(json.dumps(_new_payload, indent=4))
        tigerSqlite.Sqlite('user_events.db').update('events', [('listing', [i if int(i['id']) != int(_payload['id']) else _new_payload for i in _listing])], [('id', _owner)])
        return cls.get_event(int(_payload['id']), _user)

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

    
class belongsEvents:
    def __init__(self, _listing:typing.List[int], _user:int, _page:int = 0) -> None:
        self.listing, self.user, self.page = _listing, _user, _page
        print(self.listing, self.user, self.page)
        print('init belongsEvents')
        self.groups = [self.listing[i:i+5] for i in range(0, len(self.listing), 5)]
    
    @property
    def has_previous(self):
        return bool(self.page)

    @property
    def previous_page(self):
        if not self.has_previous:
            raise Exception
        return self.page - 1
    
    @property
    def has_next(self):
        return self.page+1 < len(self.groups)
    
    @property
    def next_page(self):
        if not self.has_next:
            raise Exception
        return self.page + 1

    def __iter__(self):
        for i in self.groups[self.page]:
            yield Events.get_event(i, self.user)

    @property
    def has_groups(self):
        return bool(self.listing)

    @classmethod
    def user_belongs_events(cls, _user:int, _page:int):
        return cls([i['id'] for a, b in tigerSqlite.Sqlite('user_events.db').get_id_listing('events') for i in b if _user in i['all_users']], _user, _page)

