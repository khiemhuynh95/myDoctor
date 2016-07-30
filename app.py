#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:

            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    #get info from sender
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text of fb user

                    #send back msg to user
                    send_typing(sender_id)
                    time.sleep(1)
                    send_message(sender_id, message_text.encode('utf-8'))
                    '''
                    if (message_text == u"chào")
                        send_message(sender_id, u"Bạn bị đau ở đâu?")
                    if (message_text == u"ngực")
                        #show button
                        show_sug_buttons(sender_id, u"Bạn có cái triệu chứng nào khác không?")    

                    '''


                    ##send_video(sender_id, "http://files.flixpress.com/5781973_2545281.mp4")

                    ##send_video(sender_id, "https://www.youtube.com/watch?v=YlLlCJxCQW8")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def show_sug_buttons(recipient_id,sug_text):
    ##log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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
         "message":{
            "attachment":{
                "type":"template",
                    "payload":{
                        "template_type":"button",
                        "text":sug_text,
                        "buttons":[
                        {
                            "type":"web_url",
                            "url":"https://petersapparel.parseapp.com",
                            "title": u"Ho ra máu"
                        },
                        {
                            "type":"postback",
                            "title": u"Đau tim",
                            "payload":"USER_DEFINED_PAYLOAD"
                         },
                         {
                            "type":"postback",
                            "title": u"Khó thở",
                            "payload":"USER_DEFINED_PAYLOAD"
                         }
                        ]
            }
        }
    }
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

def send_typing(recipient_id):
    
    log("sending message to {recipient}".format(recipient=recipient_id))

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
        "sender_action":"typing_on"
    })
    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_video(recipient_id, video_url):
    
    log("sending message to {recipient}".format(recipient=recipient_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
       "recipient":{
            "id": recipient_id
        },
        "message":{
            "attachment":{
                "type":"video",
                "payload":{
                    "url": video_url
                }
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


if __name__ == '__main__':
    app.run(debug=True)
