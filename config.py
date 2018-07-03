# Flask settings
DEBUG = True
PORT = 8080
HOST = '0.0.0.0'
SECRET_KEY = 'mysecret'

# MongoDB Settings
from pymongo import MongoClient
MONGO_DBNAME = 'trading_bot'
MONGO_URI = 'mongodb://admin:Testing123@ds221271.mlab.com:21271/trading_bot'
DATABASE = MongoClient(MONGO_URI)[MONGO_DBNAME]
USERS_COLLECTION = DATABASE.users
TRADES_COLLECTION = DATABASE.trades

# TD Ameritrade API Info
CLIENT_ID = "ATRTARGET@AMER.OAUTHAP"
REDIRECT_URI = "http://localhost:8080/tda_auth"
