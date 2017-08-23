import os
import sys
import json
import datetime
import requests
from flask import Flask, request

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
    data = request.get_json()
    log(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):

                    sender_id = messaging_event["sender"]["id"] 
                    recipient_id = messaging_event["recipient"]["id"] 
                    message_text = messaging_event["message"]["text"]  # the message's text
                    typing_indicator(sender_id)
                    sending = 'Sorry! My bot is too small to understand the phrase"' + message_text + '"'
                    if message_text.lower() == 'today':
                    	sending = getTimetable(0)
                    elif message_text.lower() == 'tomorrow':
                    	sending = getTimetable(1)
                    elif message_text.lower() == 'nextbus':
                    	sending = 'This is the latest bus schedule downloaded from http://www.iitbbs.ac.in'
                    	send_bus_schedule(sender_id)
                    send_message(sender_id, sending)

                if messaging_event.get("delivery"):
                    pass

                if messaging_event.get("optin"):
                    pass

                if messaging_event.get("postback"):
                    pass

    return "ok", 200

def typing_indicator(recipient_id):

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
	    "sender_action": "typing_on"
	})
	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	if r.status_code != 200:
	    log(r.status_code)
	    log(r.text)


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

def send_bus_schedule(recipient_id):
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
            "attachment": {
            	"type": "file",
            	"payload": {"url": "http://www.iitbbs.ac.in/transportation-fle/transport_1503241708.pdf"}
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

def getTimetable(day):
	if day == 0:
		today = datetime.datetime.today().weekday()
	elif day == 1:
		today = (datetime.datetime.today().weekday() + 1) % 7 
	if today == 0:
		return '9AM to 11 AM: Introduction to Electronics(L)\n\n11AM to 1PM: Signal and Systems(L)\n\n2:30PM to 4:30PM: Breadth-1\n\n4:30PM to 5:30PM: Introduction to Electronics(T)'
	elif today == 1:
		return '9AM to 11 AM: Data Structures(L)\n\n11AM to 12PM: Signal and Systems(T)\n\n2:30PM to 5:30PM: Introduction to Electronics(Lab)'
	elif today == 2:
		return '9AM to 10 AM: Signal and Systems(L)\n\n10AM to 11AM: Introduction to Electronics(L)\n\n11AM to 1PM: Discrete Structures(L)\n\n3:30PM to 5:30PM: Introduction to Bioscience and Technology(L)'
	elif today == 3:
		return '12PM to 1 AM: Data Structures(L)\n\n2:30PM to 5:30PM: Data Structures(Lab)'
	elif today == 4:
		return '9AM to 10 AM: Data Structures(L)\n\n10AM to 11AM: Data Structures(T)\n\n11AM to 1PM: Breadth-1\n\n2:30PM to 5:30PM:Signal and Systems(Lab)'	
	elif today == 5:
		return 'Nothing much! Enjoy your weekend :)\n\nIf you want to play CS:Go, Connect to 10.0.32.209'
	elif today == 6:
		return 'Nothing much! Enjoy your Sunday :)\n\nIf you want to play CS:Go, Connect to 10.0.32.209'

if __name__ == '__main__':
    app.run(debug=True)
