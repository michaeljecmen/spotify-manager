#!/usr/bin/python3
# run "which python3" in your terminal and
# replace "/usr/bin/python3" above with the output

from spotify.liked_songs_sliding_window.util.update_rule import get_liked_song_max, get_liked_days_max

from util.spotify import get_spotify
from util.config import read_config
from util.liked import get_previous_n_liked_songs, get_all_liked_songs_within_last_n_days
from util.playlist import find_playlist
from util.debug import set_debug, debug_print

import sys

def populate_playlist():
    config = read_config()
    spotify = get_spotify(config)
    playlist = find_playlist(config, spotify, config["LIKED_SONGS_SLIDING_WINDOW"]["SPOTIFY_SLIDING_PLAYLIST"])
    
    # songs we add initially depends on the update rule chosen by the user
    num = get_liked_song_max(config)
    if num is not None:
        liked = get_previous_n_liked_songs(spotify, num)

        # we want to add the items so future queries will appear oldest first
        # if we add the items all at the same time, they'll be newest first
        liked.reverse()
    else:
        num = get_liked_days_max(config)
        liked = get_all_liked_songs_within_last_n_days(spotify, num)
        liked = [ track['id'] for track in liked ]
        # order of tracks does not matter here

    # add songs one at a time to avoid song add limit
    for song in liked:
        spotify.playlist_add_items(playlist['id'], [ song ])
    
    debug_print(f'added {len(liked)} songs to playlist')

if __name__ == "__main__":
    set_debug(len(sys.argv) > 1)
    populate_playlist()