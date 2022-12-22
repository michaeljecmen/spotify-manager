import spotipy
from spotipy.oauth2 import SpotifyOAuth

from util.cache import ConfigCacheHandler

def get_spotify(config):
    oauth = SpotifyOAuth(client_id=config["SPOTIFY_CLIENT_ID"], client_secret=config["SPOTIFY_CLIENT_SECRET"], redirect_uri=config["SPOTIFY_REDIRECT_URI"], cache_handler=ConfigCacheHandler())
    spotify = spotipy.Spotify(oauth_manager=oauth)
    return spotify