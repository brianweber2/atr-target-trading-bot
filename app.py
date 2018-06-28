import json
import requests

from flask import Flask, abort, request
from flask_debugtoolbar import DebugToolbarExtension

from models import db
from utils import make_authorization_url
from config import CLIENT_ID, REDIRECT_URI
from exchange import TDAmeritradeAPI

td_ameritrade_api = TDAmeritradeAPI(CLIENT_ID, REDIRECT_URI)


app = Flask(__name__)
app.config.from_object(__name__)
app.config['MONGODB_SETTINGS'] = {'db': 'trading_bot'}
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'flask+mongoengine=<3'
app.debug = True
app.config['DEBUG_TB_PANELS'] = (
  'flask_debugtoolbar.panels.versions.VersionDebugPanel',
  'flask_debugtoolbar.panels.timer.TimerDebugPanel',
  'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
  'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
  'flask_debugtoolbar.panels.template.TemplateDebugPanel',
  'flask_debugtoolbar.panels.logger.LoggingPanel',
  'flask_mongoengine.panels.MongoDebugPanel'
)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db.init_app(app)

# DebugToolbarExtension(app)

@app.route('/')
def home():
  text = '<a href="{}">Authenticate with TD Ameritrade</a>'
  return text.format(make_authorization_url())

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
  app.run(debug=True, port=8080, host='0.0.0.0', ssl_context='adhoc')
