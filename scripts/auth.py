import os
import json
import spotipy
from util.config import read_config, write_config, get_absolute_spotify_repo_path

TEMP_CACHE_FILENAME = ".temp-token-cache"

# get the spotify token with the necessary credentials
# and write it to config.json for use by rolling.py
def get_and_cache_spotify_token():
    # this will require you to sign in with a web browser
    # and hit "allow access" for this app on your spotify account
    config = read_config()
    temp_cache_file = get_absolute_spotify_repo_path() + TEMP_CACHE_FILENAME
    spotipy.util.prompt_for_user_token(
        config["SPOTIFY_USERNAME"],
        "user-library-read playlist-modify-public user-top-read",
        config["SPOTIFY_CLIENT_ID"],
        config["SPOTIFY_CLIENT_SECRET"],
        config["SPOTIFY_REDIRECT_URI"],
        cache_path=temp_cache_file
    )
    
    # then read the cache file that spotipy just wrote and rewrite it to
    # our config.json file so everything's in one place
    with open(temp_cache_file, "r") as tcfile:
        spotify_token = json.load(tcfile)
    
    # store it and write it for later
    config["SPOTIFY_TOKEN"] = spotify_token
    write_config(config)
    
    # now delete the spotipy cache file
    os.remove(temp_cache_file)

if __name__ == "__main__":
    get_and_cache_spotify_token()