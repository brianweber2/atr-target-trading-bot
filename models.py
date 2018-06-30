from datetime import datetime


class User():

  def __init__(self, first_name, last_name, username, email,
               created_at, account_ids, password=''):
    self.first_name = first_name
    self.last_name = last_name
    self.username = username
    self.email = email
    self.created_at = created_at
    self.account_ids = account_ids
    self.password = password

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return True

  def get_id(self):
    return self.username
