import sys
import os
import click
import re
import random
import string

sys.path.append('../')
from config import USERS_COLLECTION
from models import User

import bcrypt

@click.command()
@click.option('--first_name', prompt="First name",
              help='The first name of the user to add.')
@click.option('--last_name', prompt="Last name",
              help='The last name of the user to add.')
@click.option('--email', prompt="Email",
              help='The email of the user to add.')
@click.option('--pass1', prompt="Password",
              help='The password of the user to add.')
@click.option('--pass2', prompt="Confirm password",
              help='Confirmation for the password of the user to add.')

def main(first_name, last_name, email, pass1, pass2):
  """Simple program that adds a new user to the MongoDB database."""
  # Strip white spaces
  first_name = first_name.strip()
  last_name = last_name.strip()
  email = email.strip()
  pass1 = pass1.strip()
  pass2 = pass2.strip()
  # Verify valid email
  if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
    print("\nInvalid email address!")
    sys.exit(0)
  # Verify email is not taken
  user_email = USERS_COLLECTION.find_one({'email': email})
  if user_email:
    print("\nEmail is already taken!")
    sys.exit(0)
  # Verify passwords match
  if pass2 != pass1:
    print("\nPasswords do not match!")
    sys.exit(0)
  # Verify strength of passwords
  if len(pass1) < 8:
    print("\nPassword must be 8 characters or longer!")
    sys.exit(0)
  # Hash password
  hashpw = bcrypt.hashpw(str.encode(pass1), bcrypt.gensalt())
  # Check if hashedpw matches unhashedpw
  if bcrypt.checkpw(str.encode(pass1), hashpw):
    pass
  else:
    print("\nPasswords do not match!")
  # Randomly generate a username and make sure it is unique
  allchar = first_name + last_name + string.digits
  username = ''.join(random.choice(allchar) for x in range(8))

  # Save user in the database
  user_obj = User(
    first_name=first_name.capitalize(),
    last_name=last_name.capitalize(),
    username=username,
    email=email,
    password=hashpw.decode('utf-8')
  )
  try:
    USERS_COLLECTION.insert_one(
      {
        '_id': user_obj.username,
        'first_name': user_obj.first_name,
        'last_name': user_obj.last_name,
        'account_ids': user_obj.account_ids,
        'email': user_obj.email,
        'created_at': user_obj.created_at,
        'password': user_obj.password
      }
    )
  except Exception as e:
    print("\nUnable to save user. Please contact support.")
    sys.exit(0)
  else:
    print("\nUser successfully created!")
    sys.exit(0)

if __name__ == '__main__':
  main()
