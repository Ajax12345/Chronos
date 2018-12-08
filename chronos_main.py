import flask, random, json, string
import chronos_users as _user, typing
import functools, chronos_calendar
import user_categories, user_calendar

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


@app.route('/user/<id>', methods=['GET'])
@isloggedin
def display_user(id):
    if int(id) == flask.session['id']:
        return flask.redirect('/profile')
    return flask.render_template('user_profile.html', visitor = _user.Users.get_user(id=int(id)), owner=_user.Users.get_user(id=int(flask.session['id'])))

@app.route('/signout')
def signout():
    _d = flask.request.args
    for i in _user.Users.headers[:-1]:
        flask.session[i] = None
    return flask.jsonify({"success":'True'})

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

@app.route('/update_profile')
def update_profile():
    _vals = json.loads(flask.request.args.get('info'))
    _name, _initials = _user.Users.update_profile(flask.session['id'], **_vals)
    return flask.jsonify({'success':'True', 'name':_name, 'initials':_initials})

@app.route('/select_users_groups')
def select_users_groups():
    return flask.jsonify({"success":"True", 'html':flask.render_template('add_users_and_groups_pannel.html')})

@app.route("/update_calendar")
def update_calendar():
    month = chronos_calendar.Calendar.month_converter(flask.request.args.get('month'))+(1 if int(flask.request.args.get('nav')) else - 1)
    year = flask.request.args.get('year')
    return flask.jsonify({'success':'True', 'html':flask.render_template('render_calendar.html', calendar=chronos_calendar.Calendar.full_calendar(month=month, year=year))})

@app.route('/filter_users')
def filter_users():
    _keyword = flask.request.args.get('keyword')
    _current_users = json.loads(flask.request.args.get('users'))
    return flask.jsonify({'success':'True', 'html':flask.render_template('filter_user_display.html', filtered=_user._searchUsers.search_users(_keyword, avoid = [flask.session['id'], *map(int, _current_users)]))})


@app.route('/calendar_settings')
def get_calendar_settings():
    return flask.jsonify({"success":"True", 'html':flask.render_template('calendar_settings.html', categories = user_categories.Categories.categories(flask.session['id']))})

@app.route('/create_category')
def create_category():
    name = flask.request.args.get('name')
    color = flask.request.args.get('color')
    border = flask.request.args.get('border')
    return flask.jsonify(user_categories.Categories.create_category(int(flask.session['id']), name, color, border))

@app.route('/create_calendar_event')
def create_calendar_event():
    data = json.loads(flask.request.args.get('data'))
    print('got data here ', data)
    user_calendar.Calendar.create_calendar_event(flask.session['id'], data)
    return flask.jsonify({"success":'True'})

@app.route('/render_categories')
def render_categories():
    return flask.jsonify({"html":flask.render_template('simple_category_render.html', categories = user_categories.Categories.categories(flask.session['id']))})

@app.route('/calendar')
@isloggedin
def display_calendar():
    return flask.render_template('user_calendar.html', user = _user.Users.get_user(id=int(flask.session['id'])))

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
