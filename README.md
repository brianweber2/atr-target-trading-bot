# ATR Target Trading Bot Web Application

This document provides a summart of the repository and how to run the ATR Target Trading Bot using Joe's studies. Note a Linux Ubuntu machine is required.

## How to install and run a virtualenv

### Install pip first

`sudo apt-get install python3-pip`

### Then install virtualenv using pip3

`sudo pip3 install virtualenv`

### Now create a virtual environment with Python3.6

`virtualenv  <name_of_env> --python=python3.6`

### Activate the virtual environment

`source <name_of_env>/bin/activate`

### Deactivate the virtual environment

`deactivate`

## Install pip_requirements.txt file

Run the following command where the pip_requirements.txt file is located:

`pip install -r pip_requirements.txt`

## Running Application

### Start Celery Scheduler

`celery beat -A app.celerybeat-schedule --loglevel=INFO --pidfile=/tmp/celerybeat.pid`

### Start Celery Worker

`celery worker -A app.celery --loglevel=INFO`

### Start Flask app (main program)

Type the following command in the top directory:

`sudo <name_of_venv>/bin/python3 app.py`
