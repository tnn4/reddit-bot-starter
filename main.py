# OAuth stuff
import random
import socket
import sys

# NOTE: This app uses PRAW:https://praw.readthedocs.io/en/stable/
import praw

# config parser
# https://docs.python.org/3/library/configparser.html#configparser.ConfigParser
import configparser

# respect rate limits

import time

import requests
import base64

# decode url
from urllib.parse import unquote

# GENERAL SETTINGS
# Set this to true if you want to use an authorized reddit instance
is_authorized=True
# turn on debug for printing
is_debug=True

# NETWORK SETTINGS
PORT=7777 # NOTE: 7777 is the default port for a Terraria server, change this if you happen to be playing Terraria online

# RATE LIMITS
# see: https://www.reddit.com/r/redditdev/comments/13wsiks/api_update_enterprise_level_tier_for_large_scale/
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

## duration
TEMPORARY="temporary"
# indicate you need permanent access for an account
PERMANENT="permanent"
RESPONSE_TYPE="code"

# INIT
praw_example_ini='praw_example.ini'
praw_ini='praw.ini'
# change this when you want to change to production
selected_ini=praw_ini
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

class Todo(Exception):
    "Raised when todo is not finished"
    
     # Call the base class constructor with the parameters it needs
    def __init__(self, message="Task is not done"):
        self.message = message
        super().__init__(self.message)
    
    pass
#ass

def todo(msg):

    raise TodoError(message=msg)
#fin

# see: https://www.reddit.com/r/redditdev/comments/71ahst/how_to_edit_my_comments_in_a_subreddit_using_praw/
def edit_user_comment_in_subreddit(r, user, subreddit):
    target_sleep_time=SLEEP_TIME
    comment_replacement="PUT REPLACEMENT TEXT HERE"
    target_subreddit=r.subreddit(subreddit)

    for comment in user.comments.new(limit=None):
        # rate limit
        time.sleep(target_sleep_time)
        #if the comment is in the wrong subreddit, continue to the next comment
        if comment.subreddit != target_subreddit:
            print('failed match: continuing')
            continue
        #fi

        print(comment.body)
        comment.edit("I'm spezzing out. Peace.")
        
        # filter for certain keywords
        if any(x in comment.body for x in ['list','of','keywords']):
            print('found keywords')
        #fi
    #rof
#fin

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


# see: https://praw.readthedocs.io/en/stable/tutorials/refresh_token.html
# https://github.com/reddit-archive/reddit/wiki/OAuth2

def get_refresh_token():
    scope_input = input(
        "Enter a comma separated list of scopes, or '*' for all scopes: "
    )
    scopes = [scope.strip() for scope in scope_input.strip().split(",")]
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        redirect_uri=redirect_url,
    )

    # unique possibly random string for each auth request
    state = str(random.randint(0,65000))
    
    # Authorization_URL: https://www.reddit.com/api/v1/authorize?client_id=CLIENT_ID&response_type=TYPE&
    # state=RANDOM_STRING&redirect_uri=URI&duration=DURATION&scope=SCOPE_STRING
    
    # TODO! This is broken
    todo("FIX - reddit authorization url")
    # I'll have to do this manually
    url = reddit.auth.url(duration=PERMANENT, scopes=scopes, state=state)
    print(f"\nOpen this url in your browser: {url}\n")
    url_fixed = f"https://www.reddit.com/api/v1/authorize?client_id={client_id}&response_type={RESPONSE_TYPE}&state={state}&redirect_url={redirect_url}&duration={PERMANENT}&scopes={scopes}"
    print(f"\nOpen this url in your browser: {url_fixed}\n")

    # NOTE nope
    decoded_url = unquote(url)
    print(f"\nOpen this url in your browser: {decoded_url}\n")

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
    print(f"returning refresh token: {refresh_token}")
    return refresh_token
#fin

# 
def get_reddit_api_object():
    pass
#fin

def main():
    
    print("Hello world! I'm a Reddit Bot.")


    if (is_debug):
        print(f'client_id: { client_id }')
        print(f"client_id: { config.get(READ_ONLY, 'client_id') }")
        print(config.get(READ_ONLY, 'client_secret'))
        print(config.get(READ_ONLY, 'user_agent'))
        print(f"redirect_uri: {redirect_uri}")
    #fi

    # Create the praw reddit object to interface with the api
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

    # create authorized instanced if we're using authorized
    if (is_authorized):
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            # Authorized
            username=username,
            password=password,
            # required for OAuth
            redirect_uri=redirect_uri,
        )
    #fi

    if (reddit.read_only):
        print("[INFO]: Your Reddit instance is Read-Only")
        print("""
[INFO]: If you want to retrieve non-public information from \
Reddit you need an `authorized instance`.
              """)
    else:
        print("[INFO]: Your Reddit instance if Authorized")
    #fi


    # OAuth2 flow

    # retrieve code to exchange for access token
    # refresh_token = get_refresh_token()
    # POST to this URL
    # include the following in your post data: grant_type=authorization_code&code=CODE&redirect_uri=URI
    access_token_url="https://www.reddit.com/api/v1/access_token"
    
    
    # create a reddit user object with our username
    reddit_user=reddit.redditor(username)
    subreddit_test='test'
    # Authorization header requires base 64 encoding
    """
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
    credentials=base64.b64encode(bytes(f"{client_id}:{client_secret}", 'utf-8'))
    # add this to the POST authorization header
    print(f"auth header content: {credentials}")
    # try editing comments
    # edit_user_comment_in_subreddit(reddit, reddit_user, subreddit_test)

    authorization_code = input(
        "Copy the authorization code from your browser: "
    )
    payload = f"""
    grant_type={authorization_code}&code=CODE&redirect_uri={redirect_uri}
    """
    # r = requests.post(access_token_url, headers={'Authorization': credentials}, data=payload)
#fin

if __name__ == "__main__":
    sys.exit(main())
#fi

"""
post with praw
https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit.submit
see: https://www.reddit.com/r/redditdev/comments/pn757n/how_to_submit_a_post_using_praw/
"""