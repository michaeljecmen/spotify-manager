from util.cache import ConfigCacheHandler
from util.debug import debug_print

from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

import requests
from typing import List


def get_spotify(config: dict) -> Spotify:
    oauth = SpotifyOAuth(client_id=config["SPOTIFY_CLIENT_ID"], client_secret=config["SPOTIFY_CLIENT_SECRET"], redirect_uri=config["SPOTIFY_REDIRECT_URI"], cache_handler=ConfigCacheHandler())
    spotify = Spotify(oauth_manager=oauth)
    return spotify


# dumb package won't even support all apis
def get_top_tracks_for_user(config: dict, limit: int = 50, time_range: str = "short_term") -> List[str]:
    """
        Gets the top <limit> songs from the user's profile. 

        Parameters:
            limit: number of tracks to fetch (default 50)
            time_range: [ "short_term", "medium_term", "long_term" ] (default short_term)
                find tracks from last 4 weeks, 6 months, and all time, respectively
    """
    params = {
        "time_range": time_range,
        "limit": limit
    }
    resp = requests.get('https://api.spotify.com/v1/me/top/tracks', headers=_get_auth_headers(config), params=params)
    debug_print("util::spotify::get_top_tracks_for_user response:", resp)
    js = resp.json()
    return js["items"]


# TODO hard pulling this from the config is not guaranteed to work, may need to refresh
def _get_auth_headers(config: dict) -> dict:
    return {
        "Authorization": f'Bearer {config["SPOTIFY_TOKEN"]["access_token"]}'
    }


def get_current_user_id(spotify: Spotify) -> str:
    return spotify.me()['id']


def get_spotify_playlist_object(spotify, username, playlist_name):
    offset = 0
    playlists = { 'next': True }
    while playlists['next']:
        playlists = spotify.user_playlists(username, limit=50, offset=offset)
        offset += len(playlists["items"])
        for playlist in playlists['items']:
            debug_print(f'found playlist {playlist["name"]}')

            # defense against taking another user's playlist that you have liked
            # not sure if this is even possible but why not
            if playlist['owner']['id'] != username:
                continue

            # only want to request the playlists once, so need to check
            # for the log playlist and the rolling playlist here and remember
            # the log playlist id
            if playlist['name'] == playlist_name:
                return playlist
    
    # yell if the playlist doesn't exist
    raise NameError(f'Error: could not find playlist with name \"{playlist_name}\"')
