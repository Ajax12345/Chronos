import flask, random, json, string
import chronos_users as _user, typing
import functools, chronos_calendar
import user_categories, user_calendar
import user_group_categories as _group_categories
import user_groups, user_events

app = flask.Flask(__name__)

app.secret_key = ''.join(random.choice(string.printable) for _ in range(10))

def isloggedin(f:typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def _wrapper(*args, **kwargs):
        if any(flask.session.get(i) is None for i in _user.Users.headers[:-1]):
            return flask.redirect('/')
        return f(*args, **kwargs)
    return _wrapper

@app.route('/', methods=['GET'])
def home():
    return flask.render_template('homepage.html')

@app.route('/login', methods=['GET'])
def login_render():
    return flask.render_template('login.html')

@app.route('/create', methods=['GET'])
@isloggedin
def create_event():
    return flask.render_template('create_event.html', user = _user.Users.get_user(id=int(flask.session['id'])))


@app.route('/signup', methods=['GET'])
def signup_render():
    return flask.render_template('signup.html')

@app.route('/dashboard', methods=['GET'])
@isloggedin
def dashboard():
    return flask.render_template('dashboard.html', user = _user.Users.get_user(id=int(flask.session['id'])))

@app.route('/register_user')
def register_user():
    _payload = json.loads(flask.request.args.get('info'))
    _result, _user_obj = _user.Users.register_user(*[_payload[i] for i in _user.Users.headers[1:-1]])
    if _result['success'] == 'True':
        for i in _user.Users.headers[:-1]:
            flask.session[i] = getattr(_user_obj, i)
    return flask.jsonify(_result)

@app.route("/navigate_timeslot_listing")
def navigate_timeslot_listing():
    _payload = json.loads(flask.request.args.get('payload'))
    return flask.jsonify({'html':flask.render_template('event_timeslot_stub.html', event=user_events.Events.get_event(int(_payload['id']), flask.session['id'], _set_timestamp = _payload['timestamp']))})


@app.route('/add_timeslot')
def add_timeslot():
    
    return flask.jsonify({'html':flask.render_template('event_timeslot_stub.html', event=user_events.Events.add_timeslot(flask.session['id'], json.loads(flask.request.args.get('payload'))))})
    #return flask.jsonify({'html':flask.render_template('event_timeslot_snippet.html', event=user_events.Events.add_timeslot(flask.session['id'], json.loads(flask.request.args.get('payload'))))})


@app.route('/add_user_availability')
def add_user_availability():
    return flask.jsonify({'html':flask.render_template('event_timeslot_stub.html', user=_user.Users.get_user(id=flask.session['id']), event = user_events.Events.add_user_availability(flask.session['id'], json.loads(flask.request.args.get('payload'))))})

@app.route('/user/<id>', methods=['GET'])
@isloggedin
def display_user(id):
    if int(id) == flask.session['id']:
        return flask.redirect('/profile')
    return flask.render_template('user_profile.html', visitor = _user.Users.get_user(id=int(id)), owner=_user.Users.get_user(id=int(flask.session['id'])))

@app.route('/delete_group_member')
def delete_group_member():
    _payload = json.loads(flask.request.args.get('payload'))
    user_groups.Groups.delete_user(flask.session['id'], int(_payload['group']), int(_payload['id']))
    return flask.jsonify({'success':"True"})

@app.route('/delete_group_subgroup')
def delete_group_subgroup():
    _payload = json.loads(flask.request.args.get('payload'))
    user_groups.Groups.delete_group(flask.session['id'], int(_payload['group']), int(_payload['id']))
    return flask.jsonify({'success':"True"})

@app.route('/user_email_visibility')
def user_email_visibility():
    getattr(_user.Users, '_'+flask.request.args.get('action').lower().replace(' ', '_'))(flask.session['id'])
    return flask.jsonify({'success':'True'})

@app.route('/event_display_details')
def event_display_details():
    payload = json.loads(flask.request.args.get('payload'))
    return flask.jsonify({'html':flask.render_template('event_details_main.html', event=user_calendar.Calendar.from_pannel_view(flask.session['id'], payload))})

@app.route('/signout')
def signout():
    _d = flask.request.args
    for i in _user.Users.headers[:-1]:
        flask.session[i] = None
    return flask.jsonify({"success":'True'})


@app.route('/update_timelisting_timestmap')
def update_timelisting_timestmap():
    flask.session[f'event_timeslot_{flask.request.args.get("id")}'] = flask.request.args.get('timestamp')
    return flask.jsonify({'success':'True'})

@app.route("/mark_as_unavailable")
def mark_as_unavailable():
    return flask.jsonify({'html':flask.render_template('event_timeslot_stub.html', event=user_events.Events.mark_unavailable(flask.session['id'], json.loads(flask.request.args.get('payload'))))})

@app.route('/user_timelisting_about')
def user_timelisting_about():
    _payload = json.loads(flask.request.args.get('payload'))
    if _payload['flag']:
        return flask.jsonify({'html':flask.render_template('more_about_user_current.html', about=user_events.About.get_about_current(_payload))})
    return flask.jsonify({"html":flask.render_template('')})


@app.route('/mark_as_available')
def mark_as_available():
    return flask.jsonify({'html':flask.render_template('event_timeslot_stub.html', event=user_events.Events.mark_available(flask.session['id'], json.loads(flask.request.args.get('payload'))))})

@app.route('/remove_set_timeslot')
def remove_set_timeslot():
    return flask.jsonify({'html':flask.render_template('event_timeslot_stub.html', event=user_events.Events.remove_timeslot(flask.session['id'], json.loads(flask.request.args.get('payload'))))})

@app.route('/event/timeslots/<id>', methods=['GET'])
@isloggedin
def event_timeslot_display(id):
    if not user_events.Events.event_exists(int(id)):
        return "<h1>Well, we thought we created a great 404 page. We failed.</h1>"
    event=user_events.Events.get_event(int(id), flask.session['id'],  _set_timestamp=flask.session.get(f'event_timeslot_{id}'))
    if not event.can_view_event:
        return flask.redirect('/')
    return flask.render_template('event_home_timeslot_display.html', event=event, user = _user.Users.get_user(id=flask.session['id']))

@app.route('/event/<id>', methods=['GET'])
@isloggedin
def display_event(id):
    if not user_events.Events.event_exists(int(id)):
        return "<h1>Well, we thought we created a great 404 page. We failed.</h1>"
    event=user_events.Events.get_event(int(id), flask.session['id'])
    if not event.can_view_event:
        return flask.redirect('/')

    return flask.render_template('event_home_display.html', event=event, user=_user.Users.get_user(id=flask.session['id']))


@app.route('/display_event_about')
def display_event_about():
    return flask.jsonify({'html':flask.render_template('event_home_about.html', event=user_events.Events.get_event(int(flask.request.args.get('id')), flask.session['id']))})


@app.route('/post_event_message')
def post_event_message():
    return flask.jsonify({"html":flask.render_template('event_home_messages.html', event=user_events.Events.post_message(flask.session['id'], json.loads(flask.request.args.get('payload'))))})

@app.route('/display_event_messages')
def display_event_messages():
    return flask.jsonify({"html":flask.render_template('event_home_messages.html', event=user_events.Events.get_event(int(flask.request.args.get('id')), flask.session['id']))})


@app.route('/login_user')
def login_user():
    _payload = json.loads(flask.request.args.get('info'))
    print('login payload', _payload)
    _response, _user_obj = _user.Users.login_user(_payload['name'], _payload['password'])
    print('login object', _user_obj)
    if _response['success'] == 'True':
        for i in _user.Users.headers[:-1]:
            flask.session[i] = getattr(_user_obj, i)
    return flask.jsonify(_response)


@app.route('/create_event')
def create_event_update():
    return flask.jsonify({'link_num':user_events.Events.create_event(flask.session['id'], json.loads(flask.request.args.get('payload')))})


@app.route('/profile', methods=['GET'])
@isloggedin
def profile():
    return flask.render_template('user_profile.html', visitor = _user.Users.get_user(id=int(flask.session['id'])), owner=_user.Users.get_user(id=int(flask.session['id'])))


@app.route('/render_event_creation_calendar')
def render_calendar():
    return flask.jsonify({'success':'True', 'calendar':flask.render_template('render_calendar.html', calendar = chronos_calendar.Calendar.full_calendar())})

@app.route('/event_privacy_settings')
def event_privacy_level():
    return flask.jsonify({'success':'True', 'html':flask.render_template('event_privacy_settings_pannel.html')})

@app.route('/profile/view', methods=['GET'])
@isloggedin
def view_profile():
    return flask.render_template('user_profile_view.html', owner=_user.Users.get_user(id=flask.session['id']), visitor=_user.Users.get_user(id=flask.session['id']))

@app.route('/groups/joined', methods=['GET'])
@isloggedin
def groups_joined():
    return flask.render_template('user_joined_groups.html', user=_user.Users.get_user(id=flask.session['id']), groups = user_groups.Groups.joined_groups(flask.session['id']))



@app.route('/group/joined/<id>')
@isloggedin
def full_group_joined_val(id):
    _result = user_groups.Groups.display_joined_group(flask.session['id'], int(id))
    return "<h1>404</h1>" if isinstance(_result, dict) else flask.render_template('individual_joined_group_display.html', user=_user.Users.get_user(id=flask.session['id']), group = _result)



@app.route('/groups', methods=['GET'])
@isloggedin
def groups():
    return flask.render_template('groups.html', user=_user.Users.get_user(id=flask.session['id']), groups=user_groups.Groups.user_groups(flask.session['id']))

@app.route('/group/<group_id>', methods=['GET'])
@isloggedin
def group_examine(group_id):
    _result = user_groups.Groups.display_group(flask.session['id'], int(group_id))
    return "<h1>Well, we thought we created a great 404 page. We failed.</h1>" if isinstance(_result, dict) else flask.render_template('individual_group_display.html', user=_user.Users.get_user(id=flask.session['id']), group = _result)

@app.route('/group_color_categories')
def group_color_categories():
    return flask.jsonify({"html":flask.render_template('group_categories.html', categories = group_categories.GroupCategories.group_categories(flask.session['id']))})

@app.route('/groups/categories', methods=['GET'])
@isloggedin
def group_categories():
    return flask.render_template('group_category_dashboard.html', user=_user.Users.get_user(id=flask.session['id']), categories = _group_categories.GroupCategories.group_categories(flask.session['id']))

@app.route('/add_group_category')
def add_group_category():
    _group_categories.GroupCategories.add_category(flask.session['id'], json.loads(flask.request.args.get('payload')))
    return flask.jsonify({"success":'True'})

@app.route('/add_users_for_groups')
def add_users_for_groups():
    return flask.jsonify({"html":flask.render_template('filter_user_display.html', filtered=_user._searchUsers.search_users(flask.request.args.get('query'), [flask.session['id']]))})

@app.route('/group_checklist_listing_creation')
def group_checklist_listing_creation():
    return flask.jsonify({'html':flask.render_template('add_groups_check_display.html', groups=user_groups.Groups.user_groups(flask.session['id']))})

@app.route('/groups/create', methods=['GET'])
@isloggedin
def create_group():
    return flask.render_template('group_create_group.html', user=_user.Users.get_user(id=flask.session['id']), categories =  _group_categories.GroupCategories.group_categories(flask.session['id']), groups=user_groups.Groups.user_groups(flask.session['id']))

@app.route('/update_profile')
def update_profile():
    _vals = json.loads(flask.request.args.get('info'))
    _result = _user.Users.update_profile(flask.session['id'], **_vals)
    print('updating result here', _result)
    return flask.jsonify({'success':'True', 'payload':json.dumps(_result)})

@app.route('/select_users_groups')
def select_users_groups():
    return flask.jsonify({"success":"True", 'html':flask.render_template('add_users_and_groups_pannel.html')})

@app.route("/update_calendar")
def update_calendar():
    month = chronos_calendar.Calendar.month_converter(flask.request.args.get('month'))+(1 if int(flask.request.args.get('nav')) else - 1)
    year = flask.request.args.get('year')
    return flask.jsonify({'success':'True', 'html':flask.render_template('render_calendar.html', calendar=chronos_calendar.Calendar.full_calendar(month=month, year=year))})

@app.route('/update_by_month_calendar')
def update_by_month_calendar():
    vals = json.loads(flask.request.args.get('vals'))
    month = chronos_calendar.Calendar.month_converter(vals['month'])+(1 if int(vals['nav']) else - 1)
    year = int(vals['year'])
    return flask.jsonify({'success':'True', 'html':flask.render_template('calendar_by_month.html', calendar=chronos_calendar.Calendar.full_calendar(month=month, year=year))})

@app.route('/filter_users')
def filter_users():
    _keyword = flask.request.args.get('keyword')
    _current_users = json.loads(flask.request.args.get('users'))
    return flask.jsonify({'success':'True', 'html':flask.render_template('filter_user_display.html', filtered=_user._searchUsers.search_users(_keyword, avoid = [flask.session['id'], *map(int, _current_users)]))})


@app.route('/calendar_settings')
def get_calendar_settings():
    return flask.jsonify({"success":"True", 'html':flask.render_template('calendar_settings.html', categories = user_categories.Categories.categories(flask.session['id']))})


@app.route('/render_mini_calendar')
def render_mini_calendar():
    return flask.jsonify({'html':flask.render_template('mini_calendar.html', calendar=chronos_calendar.Calendar.mini_calendar(flask.request.args.get('timestamp')))})

@app.route('/user_personal_event_listings')
def user_personal_event_listings():
    return flask.jsonify({'html':flask.render_template('user_personal_event_listing.html', user =  _user.Users.personal_events_pagination(int(flask.session['id']), int(flask.request.args.get('page'))))})

@app.route('/create_category')
def create_category():
    name = flask.request.args.get('name')
    color = flask.request.args.get('color')
    border = flask.request.args.get('border')
    return flask.jsonify(user_categories.Categories.create_category(int(flask.session['id']), name, color, border))

@app.route('/create_calendar_event')
def create_calendar_event():
    data = json.loads(flask.request.args.get('data'))
    user_calendar.Calendar.create_calendar_event(flask.session['id'], data)
    return flask.jsonify({"success":'True', 'html':flask.render_template('by_week_calendar.html', calendar=user_calendar.Calendar.by_week(user = int(flask.session['id']), expedient=True))})

@app.route('/by_month_event_listing')
def by_month_event_listing():
    return flask.jsonify({'success':'True', 'html':flask.render_template('by_month_calendar_pannel.html', event=user_calendar.Calendar.events_by_day(flask.session['id'], json.loads(flask.request.args.get('payload'))))})

@app.route('/delete_event')
def delete_event():
    payload = json.loads(flask.request.args.get('payload'))
    return flask.jsonify({'html':flask.render_template('by_week_calendar.html', calendar=user_calendar.Calendar.remove_event(flask.session['id'], payload))})
@app.route('/navigate_calendar_by_week')
def navigate_calendar_by_week():
    _full_data = json.loads(flask.request.args.get('values'))

    return flask.jsonify({'success':"True", 'html':flask.render_template('by_week_calendar.html', calendar=user_calendar.Calendar.navigate_week(int(flask.session['id']), _full_data))})

@app.route('/display_user_groups')
def display_user_groups():
    return flask.jsonify({"html":flask.render_template('user_group_search_display.html', groups=user_groups.Groups.user_groups(flask.session['id']))})

@app.route('/create_group')
def _create_group():
    return flask.jsonify({'linkto':user_groups.Groups.create_group(flask.session['id'], json.loads(flask.request.args.get('payload')))})


@app.route('/render_categories')
def render_categories():
    return flask.jsonify({"html":flask.render_template('simple_category_render.html', categories = user_categories.Categories.categories(flask.session['id']))})

@app.route('/dynamic_calendar_display')
def dynamic_calendar_display():
    return flask.jsonify({"success":'True', 'html':flask.render_template('by_week_calendar.html', calendar=user_calendar.Calendar.by_week(user = int(flask.session['id']), expedient=True))})


@app.route('/update_pannel_event_listing')
def update_pannel_event_listing():
    return flask.jsonify({"success":'True', 'html':flask.render_template('quick_look_html.html', event=user_calendar.Calendar.from_pannel_view(flask.session['id'], json.loads(flask.request.args.get('payload'))))})

@app.route('/by_month_calendar')
def by_month_calendar():
    return flask.jsonify({'success':'True', 'html':flask.render_template('calendar_by_month.html', calendar = chronos_calendar.Calendar.full_calendar())})


@app.route('/event_quick_look')
def event_quick_look():
    payload = json.loads(flask.request.args.get('payload'))
    print('quick look payload', payload)
    return flask.jsonify({"success":'True', 'html':flask.render_template('quick_look_html.html', event=user_calendar.Calendar.quick_look(flask.session['id'], payload))})

@app.route('/calendar')
@isloggedin
def display_calendar():
    return flask.render_template('user_calendar_stub.html', user = _user.Users.get_user(id=int(flask.session['id'])))

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.debug = True

    app.run()
