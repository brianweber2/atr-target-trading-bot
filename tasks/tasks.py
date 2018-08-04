import sys
import json
import requests
from datetime import datetime

import celery

sys.path.append('../')
from tdameritrade import td_ameritrade_api
from config import TD_AUTH_COLLECTION, CLIENT_ID


@celery.task
def keep_td_access_tokens_alive():
  """
  Background task to periodically loop through the AUTH_DB to refresh the
  access tokens if they exist.
  """
  # Get all entries in TD_AUTH_COLLECTION
  all_td_auths = TD_AUTH_COLLECTION.find()

  # If there are entries, request new token with refresh token
  if all_td_auths:
    for doc in all_td_auths:
      headers = {'Content-Type': 'application/x-www-form-urlencoded'}
      data = {
        'grant_type': 'refresh_token',
        'refresh_token': doc['refresh_token'],
        'access_type': 'offline',
        'client_id': CLIENT_ID
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
      # Update DB entry with new token info
      doc['access_token'] = access_token
      doc['refresh_token'] = refresh_token
      doc['at_expires_in'] = at_expires_in
      doc['rt_expires_in'] = rt_expires_in
      doc['lastModified'] = datetime.now()
      TD_AUTH_COLLECTION.update_one(
        {"_id": doc['_id']},
        {"$set": doc},
        upsert=False)
      # Update td_ameritrade_api object with new token info
      td_ameritrade_api.access_token = access_token
    pass
  else:
    # Do nothing
    pass

@celery.task
def execute_bot():
  """
  The main task for running the trading bot.
  """
  pass
