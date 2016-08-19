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

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    #get info from sender
                    try:    
                        sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                        message_text = messaging_event["message"]["text"]  # the message's text of fb user
                        #send_typing(sender_id)
                        #message_text = message_text.encode('utf-8')
                        message_text = message_text.encode('utf-8')
                        
                        send_message(sender_id, "Hello")
                       
                        
                    except:
                        pass
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    #pass
                    try:
                        sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                        payload = messaging_event["postback"]["payload"]  # the message's text of fb user
                        payload = payload.encode('utf-8') 
                        #service(1, sender_id, payload)
                        if (payload == u"Ngu nhiều"):
                            send_message(sender_id, u'cần muối')
                        if (payload == u"Ngu ít"):
                            send_message(sender_id, u'Thiệt không? :))')
                        if (payload == u"Không ngu"):
                            send_message(sender_id, u'éo quan tâm nhé')
                    except:
                        pass

    return "ok", 200


def service(mode, user_id, message):
    response = requests.get('http://521504a0.ngrok.io/process', {'mode': mode, 'user_id': user_id, 'message': message})
    log('response: ')
    log(response)

    if response.status_code != 200:
        return None

    content = json.loads(response.content)
    log("Content: ")
    log(content)
    log("Status: ")
    log(content['status'])

    if content['status'] == '1':
        log("It's stupid!")
        return None

    log("Ahihi")
    message = content['message']

    if content['type'] == '0': #text
        log("Received: Text")
        send_message(user_id, message.encode('UTF-8'))
    elif content['type'] == '1': #buttons
        log("Received: Buttons")
        send_buttons(user_id, message)
    elif content['type'] == '2': #video
        log("Received: Video")
        send_youtube(user_id, message)
    elif content['type'] == '3': #map
        log("Received: Map")
        send_map(user_id, message)



def send_map(recipient_id, message):
    
    log("sending message to {recipient}".format(recipient=recipient_id))

    r = []
    for msg in message:
        latitude = msg['latitude']
        longitude = msg['longitude']
        title = msg['title']
        subtitle = msg['subtitle']
        r.append({
                    'title': title,
                    'subtitle':subtitle,
                    'image_url': 'http://staticmap.openstreetmap.de/staticmap.php?center=' + latitude + ',' + longitude + '&zoom=18&size=640x480&markers=' + latitude + ',' + longitude + ',ol-marker',
                    #'image_url' : 'http://staticmap.openstreetmap.de/staticmap.php?center=10.762952,106.682340&zoom=15&size=640x480&markers=10.762952,106.682340,ol-marker',
                    'buttons': [{
                        'type': 'web_url',
                        #'url': 'http://staticmap.openstreetmap.de/staticmap.php?center=' + latitude + ',' + longitude + '&zoom=18&size=640x480&markers=' + latitude + ',' + longitude + ',ol-marker',
                        'url': 'http://maps.google.com/maps?q=loc:' + latitude + ',' + longitude + '&z=20',
                        'title': u'Hướng dẫn đường'
                    }
                ]})

    log(r)

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        'message' : {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'elements': r
                    }
                }
            }
        }
    )

    send_data(data)


def show_get_started_button():
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    data = json.dumps({

                     "setting_type":"call_to_actions",
              "thread_state":"new_thread",
              "call_to_actions":[
                {
                  "payload":"USER_DEFINED_PAYLOAD"
                }
              ]
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

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
                            "title": u"Ngu nhiều"
                        },
                        {
                            "type":"postback",
                            "title": u"Ngu ít",
                            "payload":  u"Ngu ít"
                         },
                         {
                            "type":"postback",
                            "title": u"Không ngu",
                            "payload": u"Không ngu"
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

def send_data(data):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send_buttons(recipient_id, message):
    buttons = []
    for choice in message['choices']:
        buttons.append({
                "type":"postback",
                "title": choice,
                "payload":  choice
            })

    data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
             "message":{
                "attachment":{
                    "type":"template",
                        "payload":{
                            "template_type":"button",
                            "text": message['question'],
                            "buttons": buttons
                    }   
                }
            }
        })

    log(data)
    send_data(data)


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    log(data)
    send_data(data)

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

def send_youtube(recipient_id, message):
    log("sending message to {recipient}".format(recipient=recipient_id))

    r = []
    for msg in message:
        title = msg['title']
        img_url = msg['image_url']
        subtitle = msg['subtitle']
        video_url = msg['link']

        r.append({
                    "title": title,
                    "image_url": img_url,
                    "subtitle":subtitle,
                    "buttons":[
                      {
                        "type":"web_url",
                        "url": video_url,
                        "title":"Xem"
                      }
                                  
                    ]
                })

    log(r)

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
         "message":{
            "attachment":{
                "type":"template",
                    "payload":{
                        "template_type":"generic",
                            "elements": r
                    }
                }
            }
        }
    )
    send_data(data)



def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
