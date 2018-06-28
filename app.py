from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from models import db
from utils import make_authorization_url


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

from views import home, tda_auth
app.add_url_rule('/', view_func=home)
app.add_url_rule('/tda_auth', view_func=tda_auth)

if __name__ == '__main__':
  app.run(debug=True, port=8080, host='0.0.0.0', ssl_context='adhoc')
