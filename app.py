import json
import requests

from flask import (Flask, abort, request, render_template, url_for, redirect,
                   g, flash)
from flask_pymongo import PyMongo
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)
from flask_bcrypt import check_password_hash, generate_password_hash

from models import User
from forms import RegistrationForm, LoginForm
from utils import make_authorization_url
from config import (CLIENT_ID, REDIRECT_URI, SECRET_KEY, MONGO_DBNAME,
                    MONGO_URI, DEBUG, PORT, HOST)
from exchange import TDAmeritradeAPI

td_ameritrade_api = TDAmeritradeAPI(CLIENT_ID, REDIRECT_URI)

app = Flask(__name__)

app.config['MONGO_DBNAME'] = MONGO_DBNAME
app.config['MONGO_URI'] = MONGO_URI

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mongo = PyMongo(app)

@login_manager.user_loader
def load_user(email):
  existing_user = User.objects.raw({'email': email})
  if existing_user is None:
    print("User does not exist")
    return None
  return existing_user

@app.before_request
def before_request():
  """Load current user before each request."""
  g.user = current_user

@app.after_request
def after_request(response):
  """Actions to perform after each request."""
  return response

# @app.route('/')
# def home():
#   text = '<a href="{}">Authenticate with TD Ameritrade</a>'
#   return text.format(make_authorization_url())

@app.route('/')
def index():
  if current_user in User.objects.all():
    user = current_user
    return render_template('index.html', user=user)
  else:
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  """Login user."""
  form = LoginForm()
  if form.validate_on_submit():
    user = [x for x in User.objects.raw({'_id': form.email.data})]
    try:
      user = user[0]
    except IndexError:
      flash("Your email or password don't match!", "error")
    else:
      print(user.password, form.password.data)
      if check_password_hash(user.password.encode('utf-8'), form.password.data):
        login_user(user)
        flash("You've been logged in!", "success")
        return redirect(url_for('index'))
      else:
        flash("Your email or password don't match!", "error")
  return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
  """View for a new user to register."""
  form = RegistrationForm()
  if form.validate_on_submit():
    User(
      first_name=form.first_name.data,
      last_name=form.last_name.data,
      email=form.email.data,
      password=generate_password_hash(form.password.data).decode('utf-8')
    ).save()
    flash("You have successfully registered!", "success")
    return redirect(url_for('index'))
  return render_template('register.html', form=form)

@app.route('/tda_auth')
def tda_auth():
  '''
  Auth code is sent here from TD Ameritrade's API. Use this code to receive
  access and refresh tokens. If successful, notify user then redirect to profile.
  '''
  error = request.args.get('error', '')
  if error:
    return "Error: {}".format(error)
  auth_code = request.args.get('code')

  # Post Access Token Request
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  data = {
    'grant_type': 'authorization_code',
    'access_type': 'offline',
    'code': auth_code,
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI
  }
  auth_reply = requests.post(
    'https://api.tdameritrade.com/v1/oauth2/token',
    headers=headers,
    data=data
  )
  # Responds with keys access_token, refresh_token, expires_in,
  # refresh_token_expires_in, token_type
  auth_reply_data = json.loads(auth_reply.text)
  # Set access token and other variables on Exchange object
  td_ameritrade_api.access_token = auth_reply_data['access_token']
  td_ameritrade_api.refresh_token = auth_reply_data['refresh_token']
  td_ameritrade_api.at_expires_in = auth_reply_data['expires_in']
  td_ameritrade_api.rt_expires_in = auth_reply_data['refresh_token_expires_in']
  return "Got an accesss token! {}".format(td_ameritrade_api.access_token)

if __name__ == '__main__':
  app.secret_key = SECRET_KEY
  app.run(debug=DEBUG, port=PORT, host=HOST, ssl_context='adhoc')
