import json
import requests
import urllib.parse

from flask import Flask, abort, request

from exchange import TDAmeritradeAPI

CLIENT_ID = "ATRTARGET@AMER.OAUTHAP"
REDIRECT_URI = "http://localhost:8080/tda_auth"

td_ameritrade_api = TDAmeritradeAPI(CLIENT_ID, REDIRECT_URI)

app = Flask(__name__)

def make_authorization_url():
  params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "access_type": "offline",
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
    "refresh_token": ""
  }
  url ="https://auth.tdameritrade.com/auth?" + urllib.parse.urlencode(params)
  return url

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
