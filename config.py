# Flask settings
DEBUG = True
PORT = 8080
HOST = '0.0.0.0'
SECRET_KEY = '\xd914\xca\xd7"M\xcfB\xb4W3D\r%\xe1\xcc\xdd\xc91\xaf\x1d\x08.'

# MongoDB Settings
from pymongo import MongoClient
MONGO_DBNAME = 'trading_bot'
MONGO_URI = 'mongodb://admin:Testing123@ds221271.mlab.com:21271/trading_bot'
DATABASE = MongoClient(MONGO_URI)[MONGO_DBNAME]
USERS_COLLECTION = DATABASE.users
TD_AUTH_COLLECTION = DATABASE.td_auths
TRADES_COLLECTION = DATABASE.trades

# TD Ameritrade API Info
CLIENT_ID = "TRADINGBOT@AMER.OAUTHAP"
REDIRECT_URI = "http://localhost:8080/tda_auth"

# Celery Settings
CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'rpc://'
