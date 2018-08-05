import os
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

def create_file_with_dirs(dir_path, filename):
  """
  Create a file with its directories if they don't exist on a Linux system.
  """
  filepath = os.path.join(dir_path, filename)
  if not os.path.exists(dir_path):
    os.makedirs(dir_path)
  if not os.path.exists(filepath):
    file = open(filepath, 'w')
  return filepath
