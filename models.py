from datetime import datetime

from flask_mongoengine import MongoEngine

db = MongoEngine()


class User(db.Document):
  meta = {'collection': 'user'}
  first_name = db.StringField(required=True, max_length=50)
  last_name = db.StringField(required=True, max_length=50)
  email = db.EmailField(required=True, unique=True)
  created_at = db.DateTimeField(default=datetime.now)
  account_ids = db.ListField(db.IntField())
