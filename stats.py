import os
import sys
import json
import nba_py
import requests
import pandas
from datetime import datetime, timedelta

def get_scorecard(date):
	# print(str(date.day))
	scorecard =  nba_py.Scoreboard(month=date.month, day=23, year=date.year)
	print str(scorecard.json)

if __name__ == '__main__':
    today = datetime.today()
    get_scorecard(today)
