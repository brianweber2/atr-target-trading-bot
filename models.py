from datetime import datetime

from pymongo.write_concern import WriteConcern
from pymodm import MongoModel, fields, connect

from config import MONGO_URI

# Connect to MongoDB and call the connection "my-app"
connect(MONGO_URI, alias="my-app")


class User(MongoModel):
  first_name = fields.CharField(required=True, max_length=50)
  last_name = fields.CharField(required=True, max_length=50)
  email = fields.EmailField(required=True, primary_key=True)
  created_at = fields.DateTimeField(default=datetime.now)
  password = fields.CharField(required=True, min_length=8)
  is_active = fields.BooleanField(default=True)
  account_ids = fields.ListField(fields.IntegerField())

  class Meta:
  	write_concern = WriteConcern(j=True)
  	connection_alias = 'my-app'
