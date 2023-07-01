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


# Initialization logic
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
redirect_url = config.get('Authorized', 'redirect_url')

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
            f"[ERROR]: State mismatch. Expected: {state}, Received {params["state"]}",
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
    return 0
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
        print(f"redirect_url: {redirect_url}")
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
            redirect_url=redirect_url,
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

    # create a reddit user object with our username
    reddit_user=reddit.redditor(username)
    edit_user_comment_in_subreddit(reddit, reddit_user, 'pcgaming')
#fin

if __name__ == "__main__":
    sys.exit(main())
#fi

"""
post with praw
https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit.submit
see: https://www.reddit.com/r/redditdev/comments/pn757n/how_to_submit_a_post_using_praw/
"""