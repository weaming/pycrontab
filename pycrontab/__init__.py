"""
Inspired by https://stackoverflow.com/questions/373335/how-do-i-get-a-cron-like-scheduler-in-python

Components:
* cron parser
* match time to parsed cron
* fire the task with no wait
* run task in thread pool

"""
from .parser import CronTab
from .errors import *
from .config import parse_configs_and_run

version = "0.1.0"
