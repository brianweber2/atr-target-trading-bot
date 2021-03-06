#!/home/brianweber2/Desktop/ATR-Target-Trading/app/venv/bin/python
import json
import requests
import logging
import logging.config

from flask import (Flask, abort, request, render_template, url_for, redirect,
                   g, flash, session)
from flask_pymongo import PyMongo
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)
from flask_bcrypt import check_password_hash
from flask_bootstrap import Bootstrap
from celery import Celery
import yaml

from models import User
from forms import LoginForm
from utils import make_authorization_url, create_file_with_dirs
from config import (CLIENT_ID, REDIRECT_URI, SECRET_KEY, MONGO_DBNAME,
                    MONGO_URI, DEBUG, PORT, HOST, USERS_COLLECTION,
                    TD_AUTH_COLLECTION, CELERY_BROKER_URL, CELERY_RESULT_BACKEND,
                    LOG_DIR_PATH, LOG_FILE_NAME, LOG_ERRORS_FILENAME)
from tdameritrade import td_ameritrade_api
import celeryconfig
from tasks.tasks import execute_bot


app = Flask(__name__)
# Add Bootstrap wrapper
Bootstrap(app)

# MongoDB configuration
app.config['MONGO_DBNAME'] = MONGO_DBNAME
app.config['MONGO_URI'] = MONGO_URI
mongo = PyMongo(app)

# Login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Celery configuration
app.config['CELERY_BROKER_URL'] = CELERY_BROKER_URL
app.config['CELERY_RESULT_BACKEND'] = CELERY_RESULT_BACKEND

# Initialize Celery
celery = Celery(app.name,
                backend=app.config['CELERY_RESULT_BACKEND'],
                broker=app.config['CELERY_BROKER_URL'])
celery.config_from_object(celeryconfig)
celery.conf.update(app.config)

@login_manager.user_loader
def load_user(username):
  user = USERS_COLLECTION.find_one({'_id': username})
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
    user = USERS_COLLECTION.find_one({'_id': form.username.data})

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
      logger.info('{} has been logged in.'.format(user['_id']))
      return redirect(url_for('index'))
    logger.warning('{} failed to log in.'.format(user['_id']))
    flash("Your email or password don't match!", "error")
  return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
  logger.info('{} has been logged out.'.format(current_user.username))
  logout_user()
  flash("You've been logged out!", "success")
  return redirect(url_for('login'))

@app.route('/authentication')
@login_required
def authentication():
  text = '<a href="{}">Authenticate with TD Ameritrade</a>'
  auth_url = text.format(make_authorization_url())
  return render_template('dashboard_auth.html', user=current_user,
                         auth_url=auth_url, td_access_token=td_ameritrade_api.access_token)

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
  access_token = auth_reply_data['access_token']
  refresh_token = auth_reply_data['refresh_token']
  at_expires_in = auth_reply_data['expires_in']
  rt_expires_in = auth_reply_data['refresh_token_expires_in']

  # Create or update auth tokens in auth_db for user
  user_td_auth = TD_AUTH_COLLECTION.find_one(
    {'username': current_user.username}
  )
  user_td_auth_data = {
    'username': current_user.username,
    'auth_code': auth_code,
    'access_token': access_token,
    'refresh_token': refresh_token,
    'at_expires_in': at_expires_in,
    'rt_expires_in': rt_expires_in
  }
  if not user_td_auth:
    # Create new doc
    TD_AUTH_COLLECTION.insert_one(user_td_auth_data)
  else:
    # update doc
    TD_AUTH_COLLECTION.update_one(
      {"username": current_user.username},
      {"$set": user_td_auth_data,
       "$currentDate": {"lastModified": True}})

  # Set access token and other variables on Exchange object
  td_ameritrade_api.access_token = access_token
  td_ameritrade_api.refresh_token = refresh_token
  td_ameritrade_api.at_expires_in = at_expires_in
  td_ameritrade_api.rt_expires_in = rt_expires_in

  flash("Your TD Ameritrade account has been successfully connected!",
        "success")
  return redirect(url_for('live_trading'))

if __name__ == '__main__':
  # Create logger directories and files
  create_file_with_dirs(LOG_DIR_PATH, LOG_FILE_NAME)
  create_file_with_dirs(LOG_DIR_PATH, LOG_ERRORS_FILENAME)

  # Configure logging
  with open('logging.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())
  logging.config.dictConfig(config)

  # Get logger
  logger = logging.getLogger(__name__)

  logger.info('Starting trading bot web app...')

  app.secret_key = SECRET_KEY
  app.run(debug=DEBUG, port=PORT, host=HOST, ssl_context='adhoc')
