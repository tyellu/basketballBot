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
from stats import *

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
    send_message(fb_id, text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

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

def do_action(request):
    context = request['context']
    entities = request['entities']
    query = first_entity_value(entities, 'query')
    if(query == 'games'):
        date = first_entity_value(entities, 'datetime')
        if(date):
            result = get_games(date)
            context['games_list'] = result
        else:
            pass
    elif(query == 'standings'):
        conf = first_entity_value(entities, 'conference')
        if(conf):
            result = get_standings(conf)
            context['standings'] = result
    elif(query == 'scores'):
        date = first_entity_value(entities, 'datetime')
        if(date):
            result = get_scores(date)
            context['score_list'] = result
        else:
            today = date.today()
            result = get_scores(today)
            context['score_list'] = result
    return context


#actions
actions = {
    'send' : send,
    'do_action': do_action,
    
}

client = Wit(access_token=os.environ["WIT_ACCESS_TOKEN"], actions=actions)

if __name__ == '__main__':
    app.run(debug=True)

