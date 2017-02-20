import os
import sys
import json
import requests
from flask import Flask, request
from wit import Wit
import nba_py
from nba_py import *
import pandas
from datetime import datetime, timedelta

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    client.run_actions(session_id=sender_id, message=message_text) #forwards the message to wit.ai
                    # if (message_text == "hi" or message_text == "Hi"):
                    #     send_message(sender_id, "Hello, how can I help u?")
                    

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send(request, response):
    """
    Sender function
    """
    # We use the fb_id as equal to session_id
    fb_id = request['session_id']
    text = response['text']
    # send message
    send_message(fb_id, "wit says : " + text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

def get_scorecard(request):
    context = request['context']
    entities = request['entities']
    date = first_entity_value(entities, 'datetime')
    if date:
        scorecard =  nba_py.Scoreboard(month=date[5:7], day=date[8:10], year=date[0:4])
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

    context['games_list'] = date_entity
    return context
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

#actions
actions = {
    'send' : send,
    'get_scorecard' : get_scorecard,
    
}

client = Wit(access_token=os.environ["WIT_ACCESS_TOKEN"], actions=actions)

if __name__ == '__main__':
    app.run(debug=True)

