# NOTE: This app uses PRAW:https://praw.readthedocs.io/en/stable/
import praw

# config parser
# https://docs.python.org/3/library/configparser.html#configparser.ConfigParser
import configparser

if __name__ == "__main__":
    pass
    print("Hello world! I'm a Reddit Bot.")

    # Set this to true if you want to use an authorized reddit instance
    is_authorized=True

    READ_ONLY='Read-Only'
    AUTHORIZED='Authorized'

    praw_example_ini='praw_example.ini'
    praw_ini='praw.ini'
    # change this when you want to change to production
    selected_ini=praw_example_ini

    # set up configparser to read .ini
    config = configparser.ConfigParser()
    print(f'Reading {selected_ini}')
    config.read(selected_ini)
    
    # get info for Read-Only Instance
    client_id     = config.get('Read-Only', 'client_id')
    client_secret = config.get('Read-Only', 'client_secret')
    user_agent    = config.get('Read-Only', 'user_agent')

    # get info for Authorized Instance
    username = config.get('Authorized', 'username')
    password = config.get('Authorized', 'password')


    print(f'client_id: { client_id }')
    print(f"client_id: { config.get(READ_ONLY, 'client_id') }")

    print(config.get(READ_ONLY, 'client_secret'))
    print(config.get(READ_ONLY, 'user_agent'))

    # Create the praw reddit object to interface with the api
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

    if (is_authorized):
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            # Authorized
            username=username,
            password=password,
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

#fi