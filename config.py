# Flask settings
DEBUG = True
PORT = 8080
HOST = '0.0.0.0'
SECRET_KEY = 'mysecret'

# MongoDB Settings
MONGO_DBNAME = 'trading_bot'
MONGO_URI = 'mongodb://admin:Testing123@ds221271.mlab.com:21271/trading_bot'

# TD Ameritrade API Info
CLIENT_ID = "ATRTARGET@AMER.OAUTHAP"
REDIRECT_URI = "http://localhost:8080/tda_auth"
