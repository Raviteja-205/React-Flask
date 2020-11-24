from functools import wraps
import jwt
import datetime
from flask import session
import configparser
from flask import Flask, redirect, url_for, session, render_template, request,jsonify, make_response, render_template
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisthesecretkey'

app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="296182337755-d178m2emeaimc8l6k8o4g64eo8fot8kj.apps.googleusercontent.com",
    client_secret="sL_L673Kh7Ki_HpIXxT4__3G",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get('profile', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            return f(*args, **kwargs)
        return 'You aint logged in, no page for u!'
    return decorated_function

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

@app.route('/unprotected')
def unprotected():
    return jsonify({'message' : 'Anyone can view this!'})

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message' : 'This is only available for people with valid tokens.'})


@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('signin.html')
    else:
        return 'Currently logged in'

@app.route('/login_jwt', methods=['POST'])
def login_jwt():
    # auth = request.authorization
    if request.form['username'] and request.form['password'] == 'secret':
        token = jwt.encode({'user' : request.form['username'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=60)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    else:
        return "Could not verify - Wrong Password"

@app.route('/success')
def success():
    email = dict(session)['profile']['email']
    return f'Hello, you are logged in as {email}!'

@app.route('/login_google', methods=['POST'])
def login_google():
    if request.form['username'] and request.form['password'] == 'secret':
        google = oauth.create_client('google')
        redirect_uri = url_for('authorize', _external=True)
        return google.authorize_redirect(redirect_uri)
    else:
        return "Sorruy wrong credentials"

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    user = oauth.google.userinfo()  
    session['profile'] = user_info
    session.permanent = True
    return redirect('/success')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)