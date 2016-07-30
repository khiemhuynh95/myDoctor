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
                    try:
                        sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                        message_text = messaging_event["message"]["text"]  # the message's text of fb user

                        service(1, sender_id, message_text)

                        '''
                        #send back msg to user
                        #send_typing(sender_id)
                        #time.sleep(1)
                        
                        show_get_started_button()
                        message_text = message_text.encode('utf-8')
                        #send_message(sender_id, message_text.encode('utf-8'))
                        if (message_text == "chào"):
                            send_message(sender_id, u"Chào Khiem, bạn bao nhiêu tuổi?".encode('utf-8'))
                        if (message_text == "21"):                  
                            send_message(sender_id, u"Giới tính của bạn?".encode('utf-8'))
                        if (message_text == "nam"):
                            send_message(sender_id, u"Bạn bị đau ở đâu?".encode('utf-8'))
                        if (message_text == "ngực"):
                            show_sug_buttons(sender_id, u"Bạn có cái triệu chứng nào khác không?".encode('utf-8'))    
                        if  (message_text == "yt"):
                            send_youtube(sender_id, u"Sức khỏe và đời sống" , "https://i.ytimg.com/vi/Mxx4c78HMCs/hqdefault.jpg" ,"https://www.youtube.com/watch?v=Mxx4c78HMCs")

                        if  (message_text == "Đau tim"):
                            send_message(sender_id, u"Bạn bị bệnh rồi".encode('utf-8'))
                        
                        if  (message_text == "map"):
                            send_map(sender_id, '10.762952','106.682340')
                        '''
                    except:
                        pass
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    #pass
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    payload = messaging_event["postback"]["payload"]  # the message's text of fb user
                    payload = payload.encode('utf-8') 
                    service(1, sender_id, payload)


    return "ok", 200


def service(mode, user_id, message):
    response = requests.get('http://521504a0.ngrok.io', {'mode': mode, 'user_id': user_id, 'message': message})
    if response.status_code != 200:
        return None
    response = json.loads(response.content)
    if response.status == 1:
        return None
    
    data = response.message
    if response.type == '0':
        pass
    elif response.type == '1':

        params = {
                "access_token": os.environ["PAGE_ACCESS_TOKEN"]
            }
        headers = {
                "Content-Type": "application/json"
            }

        buttons = []
        for choice in data.choices:
            buttons.add({
                    "type":"postback",
                    "title": choice,
                    "payload":  choice
                })

        data = json.dumps({
                "recipient": {
                    "id": user_id
                },
                 "message":{
                    "attachment":{
                        "type":"template",
                            "payload":{
                                "template_type":"button",
                                "text": data.question,
                                "buttons": buttons
                        }   
                    }
                }
            })
            
            r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
            if r.status_code != 200:
                log(r.status_code)
                log(r.text)

    elif response.type == '2':
        pass
    elif response.type == '3':



def send_map(recipient_id, latitude, longitude):
    
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
        'message' : {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'elements': [{
                            'title': u'Bệnh viện gần nhất',
                            'subtitle':'2 km',
                            'image_url': 'http://staticmap.openstreetmap.de/staticmap.php?center=' + latitude + ',' + longitude + '&zoom=18&size=640x480&maptype=osmarenderer&markers=' + latitude + ',' + longitude + ',ol-marker',
                            #'image_url' : 'http://staticmap.openstreetmap.de/staticmap.php?center=10.762952,106.682340&zoom=15&size=640x480&markers=10.762952,106.682340,ol-marker',
                            'buttons': [{
                                'type': 'web_url',
                                'url': 'http://choray.vn/',
                                'title': u'xem thông tin'
                            }, {
                                'type': 'web_url',
                                'url': 'http://staticmap.openstreetmap.de',
                                'title': u'hướng dẫn đường'
                            }]
                        }]
                    }
                }
        }
    })
    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


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
                            "title": u"Ho ra máu"
                        },
                        {
                            "type":"postback",
                            "title": u"Đau tim",
                            "payload":  u"Đau tim"
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

def send_youtube(recipient_id, video_name ,img_url,video_url):
    
    log("sending message to {recipient}".format(recipient=recipient_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }


    r = []
    for _ in range(0, 5):
        r.append({
                                "title": video_name,
                                "image_url": img_url,
                                "subtitle":"www.youtube.com",
                                "buttons":[
                                  {
                                    "type":"web_url",
                                    "url": video_url,
                                    "title":"xem video"
                                  }
                                              
                                ]
                            })


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
    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)



def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
