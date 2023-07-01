# NOTE to run this in REPL
# import examples
# examples.<function-name()>

import os

# OAuth stuff
import random
import socket
import sys

# NOTE: This app uses PRAW:https://praw.readthedocs.io/en/stable/
import praw

# config parser
# https://docs.python.org/3/library/configparser.html#configparser.ConfigParser
import configparser

# respect rate limit of 1 request/ sec
# see: https://www.reddit.com/r/redditdev/comments/13wsiks/api_update_enterprise_level_tier_for_large_scale/
import time

print(f"[{os.path.basename(__file__)}] Hello world!")

# GENERAL SETTINGS
# Set this to true if you want to use an authorized reddit instance
is_authorized=True
# turn on debug for printing
is_debug=True

# NETWORK SETTINGS
PORT=7777 # NOTE: 7777 is the default port for a Terraria server, change this if you happen to be playing Terraria online

# RATE LIMITS
# With oauth, 100 queries / 60 sec, or wait 0.6 sec/ query
# with no oauth, 10 queries/ 60 sec or wait 6 sec/ query
sec=60
queries=100
OPTIMAL_SLEEP_TIME=sec/queries
BUFFERED_OPTIMAL_SLEEP_TIME=sec/queries * 1.5 
SLEEP_TIME=1

# praw.ini data
READ_ONLY='Read-Only'
AUTHORIZED='Authorized'

#OAUTH2
TEMPORARY="temporary"
# indicate you need permanent access for an account
PERMANENT="permanent"


# INIT
praw_example_ini='praw_example.ini'
praw_ini='praw.ini'
# change this when you want to change to production
selected_ini=praw_example_ini
# set up configparser to read .ini
config = configparser.ConfigParser()
print(f'Configuring settings using: {selected_ini}')
config.read(selected_ini)

# get info for Read-Only Instance
client_id     = config.get('Read-Only', 'client_id')
client_secret = config.get('Read-Only', 'client_secret')
user_agent    = config.get('Read-Only', 'user_agent')
# get info for Authorized Instance
username     = config.get('Authorized', 'username')
password     = config.get('Authorized', 'password')
redirect_uri = config.get('Authorized', 'redirect_uri')
# END_INIT

def handle_connection():
    """
    Wait for and then return a connected socket..

    Opens a TCP connection on port 7777, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    # check NETWORK_SETTINGS to see what ports we're using
    print(f"Server binding to http://127.0.0.1:{PORT}")
    server.bind(("127.0.0.1", PORT))
    
    client = server.accept()[0]
    server.close()
    
    return client
#fin

def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()
#fin

def get_refresh_token_example():
    scope_input = input(
        "Enter a comma separated list of scopes, or '*' for all scopes: "
    )
    scopes = [scope.strip() for scope in scope_input.strip().split(",")]
    reddit = praw.Reddit(
        user_agent="I'm a Bot by /u/BotMaster5000",
        redirect_url="http://127.0.0.1:7777"
    )

    # unique possibly random string for each auth request
    state = str(random.randint(0,65000))
    url = reddit.auth.url(duration=PERMANENT, scopes=scopes, state=state)
    print(f"Open this url in your browser: {url}")
    client = handle_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split("", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key,value) in [token.split("=") for token in param_tokens]
    }

    # state mismatch
    if state != params["state"]:
        send_message(
            client,
            f"[ERROR]: State mismatch. Expected: {state}, Received {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(
            client,
            params["error"]
        )
        return 1
    #fi

    refresh_token = reddit.auth.authorize(params["code"])
    send_message(
        client,
        f"Refresh token: {refresh_token}"
    )
    return refresh_token
#fin

def submit_link_post():

    title = "PRAW documentation"
    url = "https://praw.readthedocs.io"
    reddit.subreddit("test").submit(title, url=url)
#fin

def show_base64encoding_note():
    print(
    """
    see: https://en.wikipedia.org/wiki/Basic_access_authentication
    When the user agent wants to send authentication credentials to the server, it may use the Authorization header field.

    The Authorization header field is constructed as follows:[9]

    The username and password are combined with a single colon (:). This means that the username itself cannot contain a colon.
    The resulting string is encoded into an octet sequence. The character set to use for this encoding is by default unspecified, as long as it is compatible with US-ASCII, but the server may suggest use of UTF-8 by sending the charset parameter.[9]
    The resulting string is encoded using a variant of Base64 (+/ and with padding).
    The authorization method and a space character (e.g. "Basic ") is then prepended to the encoded string.

    For example, if the browser uses Aladdin as the username and open sesame as the password, then the field's value is the Base64 encoding of Aladdin:open sesame, or QWxhZGRpbjpvcGVuIHNlc2FtZQ==. Then the Authorization header field will appear as:

    Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ== 

    Base64(client_id:client_secret)
    """
    )
#fin