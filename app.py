import urllib.parse

from flask import Flask, abort, request

from exchange import TDAmeritradeAPI

CLIENT_ID = "ATRTARGET@AMER.OAUTHAP"
REDIRECT_URI = "http://localhost:8080/tda_auth"

app = Flask(__name__)

@app.route('/')
def home():
  text = '<a href="{}">Authenticate with TD Ameritrade</a>'
  return text.format(make_authorization_url())

def make_authorization_url():
  params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "access_type": "offline",
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
    "refresh_token": ""
  }
  # url = "https://api.tdameritrade.com/v1/oauth2/token"
  url ="https://auth.tdameritrade.com/auth?" + urllib.parse.urlencode(params)
  return url

@app.route('/tda_auth')
def tda_auth():
  error = request.args.get('error', '')
  if error:
    return "Error: {}".format(error)

  code = request.args.get('code')
  return "Got a code! {}".format(code)

if __name__ == '__main__':
  app.run(debug=True, port=8080, host='0.0.0.0', ssl_context='adhoc')
