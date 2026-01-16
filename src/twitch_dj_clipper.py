import housey_logging
housey_logging.configure()

import logging
import socket
import requests
import time
import threading
from flask import Flask, request
import ssl
from subprocess import call
from werkzeug.serving import make_server
import json
import datetime
import sys
import os
from os.path import exists
import config_loader

#variables
sock = socket.socket()
server = 'irc.chat.twitch.tv'
port = 6667
current_date = datetime.datetime.today().strftime('%Y-%m-%d')
clips_file = os.path.join("clip timestamps",f"clips-{current_date}.txt")

class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('localhost', 8888, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server')
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

def start_server():
    global server
    app = Flask('myapp')

    @app.route('/')
    def webhook():
            token_request = request.query_string
            print("Data received from Webhook is: ", request)
            return(f"{token_request}, you can now close this tab")
            
    server = ServerThread(app)
    server.start()
    print('server started')

def stop_server():
    global server
    server.shutdown()

def clip(broadcaster_id: int, token: str):

    get_stream_response = requests.get(f"https://api.twitch.tv/helix/streams?&user_id={broadcaster_id}", headers={'Authorization':f"Bearer {token}", 'Client-Id':config.twitch_api_id})
    get_stream_json = get_stream_response.json()

    try: 
        if str(get_stream_json["data"][0]["type"]).lower() == "live":
            is_live = True
    
    except:
        sock.send(f"PRIVMSG #{config.channel} : {config.channel} is not live \n".encode('utf-8'))
        logging.debug(f"{config.channel} is not live")
    
    if is_live:

        started_time = get_stream_json["data"][0]["started_at"]
        started_time = datetime.datetime.fromisoformat(started_time)
        started_timestamp = int(started_time.timestamp())
        current_time = datetime.datetime.now()
        current_timestamp = int(current_time.timestamp())

        elapsed_timestamp = current_timestamp - started_timestamp

        hours, remainder = divmod(elapsed_timestamp, 3600)
        minutes, seconds = divmod(remainder, 60)
        elapsed_time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        if not exists(clips_file):
            with open(clips_file, 'w') as File:
                File.write("")

        with open(clips_file, 'a') as File:
            File.write(f"{elapsed_time_formatted}\n")

        sock.send(f"PRIVMSG #{config.channel} : saved timestap for clip {elapsed_time_formatted} \n".encode('utf-8'))
        logging.debug(f"saved timestap for clip {elapsed_time_formatted}")
    else:

        sock.send(f"PRIVMSG #{config.channel} : {config.channel} is not live \n".encode('utf-8'))
        logging.debug(f"{config.channel} is not live")

def get_token():
        
        print("Requesting new api auth token from twitch")
        response=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(config.twitch_api_id), "client_secret" : str(config.twitch_api_secret), "grant_type":"client_credentials"})
        if "200" in str(response):
            token_json = response.json()
            token = token_json["access_token"]
        else:
            print(f"unable to request new twitch api auth token with response: {response}")
            token = "empty"
        return(token)

def check_mod_or_broadcaster(message_headers: str) -> bool:
    if "mod=1" in message_headers or "broadcaster/1" in message_headers:
        return(True)
    else:
        return(False)

def get_username(resp: str):
    username = resp.split("!", 1)
    username = username[0].split(":")
    username = str(username[-1])

    logging.debug(f"username seperated from message: {username}\n")
    return(username)

def get_ids(token: str) -> tuple[int,int]:
    # gets user id for broadcaster and bot
    getbroadcaster_response = requests.get(f"https://api.twitch.tv/helix/users?login={config.channel}", headers={'Authorization':f"Bearer {token}", 'Client-Id':config.twitch_api_id})
    getbroadcaster_responsejson = getbroadcaster_response.json()
    broadcaster_id = getbroadcaster_responsejson["data"][0]["id"]
    getbot_response = requests.get(f"https://api.twitch.tv/helix/users?login={config.bot_name}", headers={'Authorization':f"Bearer {token}", 'Client-Id':config.twitch_api_id})
    getbot_responsejson = getbot_response.json()
    bot_id = getbot_responsejson["data"][0]["id"]
    return(broadcaster_id,bot_id)

# main 
def main():
    # gets token from twitch
    token = get_token()

    broadcaster_id, bot_id = get_ids(token)

    # connects to twitch irc
    sock.connect((server, port))
    sock.send(f"PASS oauth:{config.oath_token}\n".encode('utf-8'))
    sock.send(f"NICK {config.bot_name}\n".encode('utf-8'))
    sock.send(f"JOIN #{config.channel}\n".encode('utf-8'))
    sock.send(f"CAP REQ :twitch.tv/tags twitch.tv/commands\n".encode('utf-8'))

    # main loop reading message
    while True:
        # gets messages in chat
        resp = sock.recv(2048).decode('utf-8')
        logging.debug(resp)
        # returns pong when twitch sends a ping to keep connection alive
        if resp.startswith('PING'):
            print(f"Ping message from twitch: {resp}")
            sock.send("PONG\n".encode('utf-8'))

        elif len(resp) > 0 and "PRIVMSG" in resp:
            message_headers, message = resp.split("PRIVMSG", 1)
            username = get_username(resp)

            if "!clip" in message:
                logging.debug(f"triggered clip for {username}")

                if check_mod_or_broadcaster(message_headers):
                    clip(broadcaster_id, token)
                else:
                    sock.send(f"PRIVMSG #{config.channel} : Sorry {username}, you dont have enough rights to create a clip \n".encode('utf-8'))

            if "!getclip" in message:
                sock.send(f"PRIVMSG #{config.channel} : Open source, locally hosted, what more do you want? https://github.com/keyboardmedicNL/twitch_dj_clipper \n".encode('utf-8'))

if __name__ == "__main__":
    # log exceptions
    sys.excepthook = housey_logging.log_exception

    config = config_loader.load_config()
    main()
