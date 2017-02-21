import os
import sys
import json
import nba_py
from nba_py import *
import requests
import pandas
from datetime import datetime, timedelta,date
from wit import Wit

#Global Variables
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

def get_games(request):
    context = request['context']
    entities = request['entities']
    date = first_entity_value(entities, 'datetime')
    scorecard =  nba_py.Scoreboard(month=int(date[5:7]), day=int(date[8:10]), year=int(date[0:4]))
    scoreboard = scorecard.json
    result_set = scoreboard['resultSets']
    today_games = result_set[0]['rowSet']
    game_id_index = 2
    hometeam_id_index = 6
    awayteam_id_index = 7
    game_time_index = 4
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
    for games in games_list[0:-1] :
        g_list += (games + '\n')
    if(len(g_list) != 0):
        g_list += games_list[-1]
        context['games_list'] = g_list
    else:
        context['games_list'] = 'unavilable'
    # print(g_list)

    return context


def get_standings(conf):
    context = request['context']
    entities = request['entities']
    conf = first_entity_value(entities, 'conference')
    today = date.today()
    scorecard = nba_py.Scoreboard(month=today.month, day=today.day, year=today.year)
    standings = None
    if(conf != ''):
        if(conf[0] == 'e' or conf[0] == 'E'):
            standings = scorecard.east_conf_standings_by_day()
        elif(conf[0] == 'w' or conf[0] == 'W'):
            standings = scorecard.west_conf_standings_by_day()
    std = standings.iloc[:,5 : 9 ]
    headers=['Team', 'GP', 'W', 'L']
    std_str = ''
    temp_str = ' '.join(map(str, headers))
    std_str += (temp_str + "\n")
    for row in std.values[0:-1]:
        temp_str = ' '.join(map(str, row))
        std_str += (temp_str + "\n")
    if(len(std.values) != 0):
        temp_str = ' '.join(map(str, std.values[-1]))
        std_str += (temp_str + "\n")
    print(std_str)
    context['standings'] = std_str
    return(context)


# if __name__ == '__main__':
#     get_standings("east")



