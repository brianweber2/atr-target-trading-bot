import json
import requests

from flask import (Flask, abort, request, render_template, url_for, redirect,
                   g, flash)
from flask_pymongo import PyMongo
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)
from flask_bcrypt import check_password_hash
from flask_bootstrap import Bootstrap

from models import User
from forms import LoginForm
from utils import make_authorization_url
from config import (CLIENT_ID, REDIRECT_URI, SECRET_KEY, MONGO_DBNAME,
                    MONGO_URI, DEBUG, PORT, HOST)
from exchange import TDAmeritradeAPI

td_ameritrade_api = TDAmeritradeAPI(CLIENT_ID, REDIRECT_URI)

app = Flask(__name__)
Bootstrap(app)

app.config['MONGO_DBNAME'] = MONGO_DBNAME
app.config['MONGO_URI'] = MONGO_URI

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mongo = PyMongo(app)

@login_manager.user_loader
def load_user(username):
  users = mongo.db.users
  user = users.find_one({'_id': username})
  if not user:
    flash("User does not exist")
    return None
  return User(
    first_name=user['first_name'],
    last_name=user['last_name'],
    username=user['_id'],
    email=user['email'],
    account_ids=user['account_ids'],
    created_at=user['created_at']
  )

@app.before_request
def before_request():
  g.user = current_user

# @app.route('/')
# def home():
#   text = '<a href="{}">Authenticate with TD Ameritrade</a>'
#   return text.format(make_authorization_url())

@app.route('/')
def index():
  if current_user.is_authenticated:
    return render_template('dashboard_home.html', user=current_user)
  else:
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  """Login user."""
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate_on_submit():
    users = mongo.db.users
    user = users.find_one({'_id': form.username.data})

    if user and check_password_hash(user['password'], form.password.data):
      user_obj = User(
        first_name=user['first_name'],
        last_name=user['last_name'],
        username=user['_id'],
        email=user['email'],
        account_ids=user['account_ids'],
        created_at=user['created_at']
      )
      login_user(user_obj)
      # flash("You've been logged in!", "success")
      return redirect(url_for('index'))
    flash("Your email or password don't match!", "error")
  return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  flash("You've been logged out!", "success")
  return redirect(url_for('login'))

@app.route('/authentication')
@login_required
def authentication():
  return render_template('dashboard_auth.html', user=current_user)

@app.route('/live_trading')
@login_required
def live_trading():
  return render_template('dashboard_live_trading.html', user=current_user)

@app.route('/bot_settings')
@login_required
def bot_settings():
  return render_template('dashboard_bot_settings.html', user=current_user)

@app.route('/trade_history')
@login_required
def trade_history():
  return render_template('dashboard_trade_history.html', user=current_user)

@app.route('/invoices')
@login_required
def invoices():
  return render_template('dashboard_invoices.html', user=current_user)

@app.route('/support')
@login_required
def support():
  return render_template('dashboard_support.html', user=current_user)

@app.route('/tda_auth')
@login_required
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
