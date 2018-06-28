import urllib.parse

from config import CLIENT_ID, REDIRECT_URI


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
