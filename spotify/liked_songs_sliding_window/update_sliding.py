import sys
from spotify.liked_songs_sliding_window.util.update_rule import get_liked_song_max, get_liked_days_max

from util.config import read_config
from util.spotify import get_spotify, get_spotify_playlist_object
from util.playlist import is_max_change_count_error, rotate_playlist
from spotify.liked_songs_sliding_window.liked import get_previous_n_liked_songs, get_all_liked_songs_within_last_n_days
from util.debug import debug_print
from util.gmail import debug_print_and_email_message, email_error

# given a playlist, returns the full tracklist as a list of track ids
def fetch_full_tracklist(spotify, playlist):
    tracklist = []

    current_track_offset = 0
    TRACKS_PER_PAGE = 100
    spotify_tracks = spotify.playlist_items(playlist['id'], limit=TRACKS_PER_PAGE, offset=current_track_offset)

    while spotify_tracks and spotify_tracks['items']:
        # not quite sure why the for loop is needed here
        for item in spotify_tracks['items']:
            spotify_track = item['track']
            tracklist.append(spotify_track['id'])
            
        current_track_offset += TRACKS_PER_PAGE
        spotify_tracks = spotify.playlist_items(playlist['id'], limit=TRACKS_PER_PAGE, offset=current_track_offset)
        
    return tracklist

# returns the playlist's track ids, in playlist order, and the playlist id
def get_tracklist(config, spotify, playlist_name):
    playlist = get_spotify_playlist_object(spotify, config["SPOTIFY_USERNAME"], playlist_name)

    # by default these are sorted by most recent first, if I rearrange the songs
    # in the playlist manually the invariant can be broken and the alg will break.
    # TODO account for that and go based off timestamps when added to the playlist (or
    # keep some state which tracks strict order of songs liked)

    return fetch_full_tracklist(spotify, playlist), playlist['id']

def update_playlist_song(spotify, sliding_tracklist, sliding_playlist_id, liked_songs):
    i = 0
    while liked_songs[i] not in sliding_tracklist:
        # add liked song to spotify playlist
        spotify.playlist_add_items(sliding_playlist_id, [ liked_songs[i] ])

        # remove next item in sliding_tracklist from spotify playlist 
        spotify.playlist_remove_all_occurrences_of_items(sliding_playlist_id, [ sliding_tracklist[i] ])

        i += 1
    
    # debug_print(f'made {i} changes to sliding window playlist')

def update_playlist_days(spotify, sliding_tracklist, sliding_playlist_id, liked_songs):
    liked_ids = [ song['id'] for song in liked_songs ]
    liked_set = set(liked_ids)
    sliding_set = set(sliding_tracklist)

    # one call per 100 tracks instead of one per track. every call is an edit,
    # and spotify caps a playlist's lifetime edits
    to_remove = [ track_id for track_id in sliding_tracklist if track_id not in liked_set ]
    for i in range(0, len(to_remove), 100):
        spotify.playlist_remove_all_occurrences_of_items(sliding_playlist_id, to_remove[i:i+100])
    debug_print(f'removed {len(to_remove)} tracks')

    # liked songs come newest first, so insert at the top to keep the playlist newest first
    to_add = [ track_id for track_id in liked_ids if track_id not in sliding_set ]
    for i in range(0, len(to_add), 100):
        spotify.playlist_add_items(sliding_playlist_id, to_add[i:i+100], position=i)
    debug_print(f'added {len(to_add)} tracks')

def update_liked_songs_playlist(config: dict) -> None:
    # get config
    config = read_config()

    # auth with spotify
    spotify = get_spotify(config)

    try:
        update_sliding_playlist(config, spotify)
    except Exception as e:
        if not is_max_change_count_error(e):
            raise
        # the playlist hit spotify's edit cap: swap in a fresh copy, then redo the update on it
        playlist = get_spotify_playlist_object(spotify, config["SPOTIFY_USERNAME"], config["LIKED_SONGS_SLIDING_WINDOW"]["SPOTIFY_SLIDING_PLAYLIST"])
        rotate_playlist(spotify, config["SPOTIFY_USERNAME"], playlist['id'])
        update_sliding_playlist(config, spotify)

def update_sliding_playlist(config: dict, spotify) -> None:
    # get tracklist for sliding by least recent
    sliding_tracklist, sliding_playlist_id = get_tracklist(config, spotify, config["LIKED_SONGS_SLIDING_WINDOW"]["SPOTIFY_SLIDING_PLAYLIST"])

    num = get_liked_song_max(config)
    if num is not None:
        # this script assumes you have liked at least n songs
        liked_songs = get_previous_n_liked_songs(spotify, num)
        update_playlist_song(spotify, sliding_tracklist, sliding_playlist_id, liked_songs)
        return

    num = get_liked_days_max(config)
    if num is None:
        debug_print("ERROR: UPDATE_CONFIG does not have a valid rule. give the README another look")
        exit()

    liked_songs = get_all_liked_songs_within_last_n_days(spotify, num)
    update_playlist_days(spotify, sliding_tracklist, sliding_playlist_id, liked_songs)

def update_main() -> None:
    try:
        config = read_config()
        update_liked_songs_playlist(config)
    except Exception:
        email_error("liked-songs-sliding-window")
        sys.exit(1)
