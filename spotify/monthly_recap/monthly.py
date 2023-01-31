from util.config import read_config
from util.spotify import get_spotify, get_top_tracks_for_user, get_current_user_id, get_spotify_playlist_object
from util.debug import debug_print

import dateutil.relativedelta
from spotipy import Spotify

import datetime
from typing import List

# TODO check periodically to see if the spotify api supports folders
# because ideally I put this in a folder
# TODO add cover image support as well

def create_monthly_playlist() -> None:
    config = read_config()
    spotify = get_spotify(config)
    n = config["MONTHLY_RECAP"]["NUMBER_OF_SONGS"]

    # get top N songs days by listen count
    top_tracks_uris = get_top_n_song_uris_for_previous_month(config, n)

    # now create the playlist
    playlist_name = create_empty_playlist(config, spotify, n)

    # now get the playlist from our profile to get its id
    playlist_uri = get_spotify_playlist_object(spotify, get_current_user_id(spotify), playlist_name)['uri']

    # and add the songs
    spotify.user_playlist_add_tracks(get_current_user_id(spotify), playlist_id=playlist_uri, tracks=top_tracks_uris)


def create_empty_playlist(config: dict, spotify: Spotify, n: int) -> str:
    fmt = config["MONTHLY_RECAP"]["NAMING_PATTERN"]
    now = datetime.datetime.now()

    # we want to use last month for the playlist name, given that's when this was for
    last_month = now - dateutil.relativedelta.relativedelta(months=1)
    playlist_name = last_month.strftime(fmt)

    # generate a killer description
    last_month_lower = last_month.strftime('%B').lower()
    year_of_last_month = last_month.strftime('%Y')
    
    current_month_lower = now.strftime('%B').lower()
    current_day = now.day
    current_year = now.year
    english_date = f'{current_month_lower} {current_day} {current_year}'

    desc = f'top {n} songs by listen count for {last_month_lower} {year_of_last_month} | auto-generated on {english_date}'

    # create the playlist
    spotify.user_playlist_create(get_current_user_id(spotify), playlist_name, description=desc)
    debug_print(f'playlist {playlist_name} created')
    return playlist_name


def get_top_n_song_uris_for_previous_month(config: dict, n: int) -> List[str]:
    # TODO support for n > limit = 50
    uris = []
    top_n_tracks = get_top_tracks_for_user(config, n)
    for track in top_n_tracks:
        debug_print("album:", track['album']['name'])
        debug_print("name:", track['name'])
        debug_print("artists:", [ artist["name"] for artist in track['artists'] ])
        debug_print("uri:", track['uri'])
        uris.append(track['uri'])
    return uris
