import os
import sys
import json
import nba_py
from nba_py import *
import requests
import pandas
from datetime import datetime, timedelta
from wit import Wit

def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
	return val['value'] if isinstance(val, dict) else val

def get_scorecard(request):
	context = request['context']
	entities = request['entities']
	date_entity = first_entity_value(entities, "datetime")
	if date_entity:
		date_time = datetime.datetime.strptime(date_entity, "%Y-%m-%d %H:%M:%S.%f")
		date = date_time.date()
		scorecard =  nba_py.Scoreboard(month=date.month, day=date.day, year=date.year)
		scoreboard = scorecard.json
		result_set = scoreboard['resultSets']
		today_games = result_set[0]['rowSet']
		game_id_index = 2
		hometeam_id_index = 6
		awayteam_id_index = 7
		game_time_index = 4
		team_details = {
			'1610612737' : "ATL",
			'1610612738' : "BOS",
			'1610612751' : 'BKN',
			'1610612766' : 'CHA',
			'1610612741' : 'CHI',
			'1610612739' : 'CLE',
			'1610612742' : 'DAL',
			'1610612743' : 'DEN',
			'1610612765' : 'DET',
			'1610612744' : 'GSW',
			'1610612745' : 'HOU',
			'1610612754' : 'IND',
			'1610612746' : 'LAC',
			'1610612747' : 'LAL',
			'1610612763' : 'MEM',
			'1610612748' : 'MIA',
			'1610612749' : 'MIL',
			'1610612750' : 'MIN',
			'1610612740' : 'NOP',
			'1610612752' : 'NYK',
			'1610612760' : 'OKC',
			'1610612753' : 'ORL',
			'1610612755' : 'PHI',
			'1610612756' : 'PHX',
			'1610612757' : 'POR',
			'1610612758' : 'SAC',
			'1610612759' : 'SAS',
			'1610612761' : 'TOR',
			'1610612762' : 'UTA',
			'1610612764' : 'WAS',
		}
		games_scheduled = {}
		for game in today_games:
			games_scheduled[game[game_id_index]] = [game[hometeam_id_index],game[awayteam_id_index],game[game_time_index]]
		games_list = []
		for key in games_scheduled:
			hometeam_id = games_scheduled[key][0]
			awayteam_id = games_scheduled[key][1]
			game_time = games_scheduled[key][2]
			games_list.append(str(team_details[str(awayteam_id)]) + " @ " 
				+ str(team_details[str(hometeam_id)]) + " at " + str(game_time))
		g_list = ''
		for games in games_list[0:-2] :
			g_list += (games + '\n')
		g_list += games_list[-1]
		if(g_list == ''):
			context['games_list'] = "Unavailable"	
		context['games_list'] = g_list

	else:
		pass

	context['games_list'] = "wit works"
	return context
# if __name__ == '__main__':
#     today = datetime.today()
#     games = get_scorecard(today)
#     print(games)
