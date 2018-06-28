import json
import requests

from flask import abort, request

from utils import make_authorization_url
from exchange import TDAmeritradeAPI
from config import CLIENT_ID, REDIRECT_URI

td_ameritrade_api = TDAmeritradeAPI(CLIENT_ID, REDIRECT_URI)


def home():
  text = '<a href="{}">Authenticate with TD Ameritrade</a>'
  return text.format(make_authorization_url())

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
