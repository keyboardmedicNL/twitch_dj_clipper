import src.housey_logging

import logging
import socket
import requests
import datetime
import os
from os.path import exists
import src.config_loader
import random
import re

#variables

server = 'irc.chat.twitch.tv'
port = 6667
oath_url = "https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=wdsrlwh9xtnmkfh64rdp6a95lrwho7&redirect_uri=http://localhost:8888&scope=channel%3Abot&state=c3ab8aa609ea11e793ae92361f002671"
token = ""

def timestamp_to_time_str(time_stamp) -> str:
    hours, remainder = divmod(time_stamp, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return(time_str)

def get_token():
        logging.debug("Requesting new api auth token from twitch")

        response=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(config.twitch_api_id), "client_secret" : str(config.twitch_api_secret), "grant_type":"client_credentials"})
        
        if response.ok:
            token_json = response.json()
            global token
            token = token_json["access_token"]
        
        else:
            raise RuntimeError(f"unable to request new twitch api auth token with response: {response}")
        
def check_mod_or_broadcaster(message_headers: str) -> bool:
    if "mod=1" in message_headers or "broadcaster/1" in message_headers:
        logging.debug("user is mod or broadcaster")
        return(True)
    else:
        logging.debug("user is NOT a mod or broadcaster")
        return(False)

def get_username(resp: str):
    username = resp.split("!", 1)
    username = username[0].split(":")
    username = str(username[-1])

    logging.debug(f"username seperated from message: {username}\n")
    return(username)

def get_ids() -> tuple[int,int]:
    # gets user id for broadcaster and bot
    getbroadcaster_response = requests.get(f"https://api.twitch.tv/helix/users?login={config.channel}", headers={'Authorization':f"Bearer {token}", 'Client-Id':config.twitch_api_id})
    getbroadcaster_responsejson = getbroadcaster_response.json()
    broadcaster_id = getbroadcaster_responsejson["data"][0]["id"]
    getbot_response = requests.get(f"https://api.twitch.tv/helix/users?login={config.bot_name}", headers={'Authorization':f"Bearer {token}", 'Client-Id':config.twitch_api_id})
    getbot_responsejson = getbot_response.json()
    bot_id = getbot_responsejson["data"][0]["id"]
    logging.debug(f"broadcaster id = {broadcaster_id} bot id = {bot_id}")
    return(broadcaster_id,bot_id)

def create_sock():
    global sock
    sock = socket.socket()
    sock.settimeout(1800)

def connect_to_irc():
    sock.connect((server, port))
    sock.send(f"PASS oauth:{config.oath_token}\n".encode('utf-8'))
    sock.send(f"NICK {config.bot_name}\n".encode('utf-8'))
    sock.send(f"JOIN #{config.channel}\n".encode('utf-8'))
    sock.send("CAP REQ :twitch.tv/tags twitch.tv/commands\n".encode('utf-8'))

def get_auth_workaround():
    logging.info("please open the following link in a browser and authorize, once done copy the acces_token value from your url in the browser to the config.yaml:")
    logging.info("https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=wdsrlwh9xtnmkfh64rdp6a95lrwho7&redirect_uri=http://localhost:8888&scope=channel%3Abot&state=c3ab8aa609ea11e793ae92361f002671")
    raise RuntimeError("restart the script once you have updated your oath_token in config.yaml")

def validate_token(token_to_validate:str = token, is_user_oath: bool = False):

    validate_token_response = requests.get("https://id.twitch.tv/oauth2/validate", headers= {'Authorization':f"Bearer {token_to_validate}"})

    if validate_token_response.ok:
        logging.debug("validated twitch api token and came back as valid")

    elif validate_token_response.status_code == 401:

        if not is_user_oath:
            logging.debug("validated twitch api token and came back as invalid")

            global token
            get_token()

        else:
            get_auth_workaround()

def recv_socket_message() -> str :
    response = sock.recv(2048).decode('utf-8')
    return(response)

def reconnect_sock(error_count: int):
    times_reconnected = error_count + 1
    sock.close()
    create_sock()
    connect_to_irc()
    return(times_reconnected)

def handle_resp(response_raw: str) -> str:
        return(response_raw.splitlines())

def log_messages(username: str,message: str):
    if config.log_messages:
        message_trimmed = message.split(":",1)[1]
        with open ("config/chat_log.log", "a") as chat_file:
            chat_file.write(f"{datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %X")}: {username}: {message_trimmed}\n")

def create_chat_log():
    if config.log_messages:
        chat_log = "config/chat_log.log"
        if not exists(chat_log):
            with open (chat_log, "w") as chat_file:
                chat_file.write("")
        
            
# twitch commands logic
def clip(broadcaster_id: int, message_headers: str, username: str, message: str):
    logging.debug(f"triggered clip for {username}")
    is_live = False
    clip_title = "no_title"

    if check_mod_or_broadcaster(message_headers):

        api_call_succes = False
        error_count = 0

        # error handling for twitch api calls
        while not api_call_succes:
            get_stream_response = requests.get(url=f"https://api.twitch.tv/helix/streams?&user_id={broadcaster_id}",headers={'Authorization':f"Bearer {token}", 'Client-Id':config.twitch_api_id})
            
            if get_stream_response.ok:
                api_call_succes = True
            else:
                error_count = error_count + 1
                validate_token(token)
            
            if error_count >= 5:
                raise RuntimeError("tried 5 times to complete twitch api request and failed")

        get_stream_json = get_stream_response.json()

        try: 
            if str(get_stream_json["data"][0]["type"]).lower() == "live":
                is_live = True
                logging.debug(f"{config.channel} is live")
        
        except:
            sock.send(f"PRIVMSG #{config.channel} : @{username} {config.channel} is not live \n".encode('utf-8'))
            logging.debug(f"{config.channel} is not live")
        
        if is_live:
            started_time = get_stream_json["data"][0]["started_at"]
            started_time = datetime.datetime.fromisoformat(started_time)
            started_timestamp = int(started_time.timestamp())
            started_date = f"{started_time.year}-{started_time.month:02d}-{started_time.day:02d}-{started_time.hour:02d}"

            current_time = datetime.datetime.now()
            current_timestamp = int(current_time.timestamp())
            elapsed_timestamp = current_timestamp - started_timestamp
            elapsed_time_formatted = timestamp_to_time_str(elapsed_timestamp)

            clips_file = os.path.join("clip_timestamps",f"clips-{started_date}.txt")

            if clip_title_match := re.findall("!clip (.*)$", message, re.MULTILINE | re.IGNORECASE): 
                clip_title = str(clip_title_match[0])

            os.makedirs("clip_timestamps", exist_ok=True)

            if not exists(clips_file):
                with open(clips_file, 'w') as File:
                    File.write("")

            with open(clips_file, 'a') as File:
                File.write(f"{elapsed_timestamp},{username},{clip_title}\n")

            sock.send(f"PRIVMSG #{config.channel} :MrDestructoid saved timestamp for clip {elapsed_time_formatted} MrDestructoid\n".encode('utf-8'))
            logging.debug(f"saved timestamp for clip {elapsed_time_formatted} with title {clip_title} for user {username} in file {clips_file}")
    
    else:
        sock.send(f"PRIVMSG #{config.channel} : Sorry @{username}, you dont have enough rights to create a clip \n".encode('utf-8'))

def get_clip(username: str):
    logging.debug(f"triggered getclip for {username}")
    sock.send(f"PRIVMSG #{config.channel} : @{username} Open source, locally hosted, what more do you want? https://github.com/keyboardmedicNL/twitch_dj_clipper \n".encode('utf-8'))

def clip_help(username: str):
    logging.debug(f"triggered cliphelp for {username}")
    sock.send(f"PRIVMSG #{config.channel} : @{username} !clip <clip title> to save a clip timestamp with a title, !getclip to get the link to this bots github page, !stick to see how big your stick is \n".encode('utf-8'))

def stick(username: str):
    logging.debug(f"triggered clip for {username}")
    sock.send(f"PRIVMSG #{config.channel} : @{username} has a {random.randint(3,400)} cm stick! \n".encode('utf-8'))

# main 
def main():

    global config
    config = src.config_loader.load_config()

    global token
    get_token()

    validate_token(config.oath_token,True)

    broadcaster_id, bot_id = get_ids()

    create_sock()
    connect_to_irc()

    error_count = 0

    # main loop reading message
    while True:
        if error_count == 3:
            raise RuntimeError("tried to reconnect to chat 3 times and failed")

        try:

            # gets messages in chat and splits them to a list incase multiple messages came in at the same time
            response_raw = recv_socket_message()

            if len(response_raw) > 0:
                error_count = 0
                response_list = handle_resp(response_raw)

                for resp in response_list:
                    logging.debug(f"processing message: {resp}")
                    # returns pong when twitch sends a ping to keep connection alive
                    if resp.startswith('PING'):
                        logging.debug(f"Ping message from twitch: {resp}")
                        sock.send("PONG\n".encode('utf-8'))

                    elif resp == ':tmi.twitch.tv RECONNECT':
                        logging.debug(f"RECONNECT message from twitch: {resp}")
                        error_count = reconnect_sock(error_count)
                    
                    elif resp == ':tmi.twitch.tv NOTICE * :Login unsuccessful':
                        raise RuntimeError("was unable to log in to twitch irc, this probably means your oath token is invalid")

                    #if "tmi.twitch.tv CAP * ACK :twitch.tv/tags twitch.tv/commands" in resp:
                    #    sock.send(f"PRIVMSG #{config.channel} : clipper ready to go! MrDestructoid  \n".encode('utf-8'))

                    elif (len(resp) > 0 and "PRIVMSG" in resp) and (not config.quiet):
                        message_headers, message = resp.split("PRIVMSG", 1)
                        username = get_username(resp)

                        if "!clip" in message:
                            clip(broadcaster_id, message_headers, username, message)

                        if "!getclip" in message:
                            get_clip(username)

                        if "!stick" in message:
                            stick(username)

                        if "!cliphelp" in message:
                            clip_help(username)

        except socket.timeout:
            # logic to check if connection is still up or if a reconnect is needed
            try:
                logging.debug("socket timed out, sending PING to check connection")

                sock.send("PING\n".encode('utf-8'))

                response_raw = recv_socket_message()

                if len(response_raw) > 0:
                        
                    if "PONG" in response_raw:
                        logging.debug(f"server responded: {response_raw}")
                        pass

                    else:
                        logging.debug("attempting to reconnect to chat")
                        error_count = reconnect_sock(error_count)

            except socket.timeout:
                logging.debug("attempting to reconnect to chat")
                error_count = reconnect_sock(error_count)

            except Exception as e:
                raise RuntimeError(e)
            
                
