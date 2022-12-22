#!/usr/bin/python3
# run "which python3" in your terminal and
# replace "/usr/bin/python3" above with the output

from util.config import read_config, get_liked_days_max, get_liked_song_max
from util.spotify import get_spotify
from util.liked import get_previous_n_liked_songs, get_all_liked_songs_within_last_n_days
from util.debug import set_debug, debug_print

import sys

# given a playlist, returns the full tracklist as a list of track ids
def fetch_full_tracklist(spotify, playlist):
    tracklist = []
    results = spotify.playlist(playlist['id'], fields="tracks,next")
    spotify_tracks = results['tracks']
    while spotify_tracks:
        # not quite sure why the for loop is needed here
        for item in spotify_tracks['items']:
            spotify_track = item['track']
            tracklist.append(spotify_track['id'])
            
        spotify_tracks = spotify.next(spotify_tracks)
        
    return tracklist

# returns list of { "name": trackname, "uri": uri }
# containing each song in the spotify playlist provided
def get_tracklist(config, spotify, playlist_name):
    spotify_username = config["SPOTIFY_USERNAME"]
    playlists = spotify.user_playlists(spotify_username)
    tracklist = {}
    sliding_playlist_id = ""
    for playlist in playlists['items']:
        # defense against taking another user's playlist with the same name that 
        # you have liked not sure if this is even possible but why not
        if playlist['owner']['id'] != spotify_username:
            continue

        if playlist['name'] == playlist_name:
            tracklist = fetch_full_tracklist(spotify, playlist)
            sliding_playlist_id = playlist['id']
            break

    # by default these are sorted by most recent first, if I rearrange the songs
    # in the playlist manually the invariant can be broken and the alg will break.
    # TODO account for that and go based off timestamps when added to the playlist (or
    # keep some state which tracks strict order of songs liked)

    return tracklist, sliding_playlist_id

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
    # go through sliding_tracklist and remove each one that's not in liked songs
    debug_print(f'SLIDING TRACKLIST: {sliding_tracklist}')
    for track_id in sliding_tracklist:
        debug_print(f'for track {track_id}')
        found = False
        for liked_dict in liked_songs:
            if liked_dict['id'] == track_id:
                found = True
                break
        debug_print(f'\tfound: {found}')

        if not found:
            spotify.playlist_remove_all_occurrences_of_items(sliding_playlist_id, [ track_id ])
            debug_print("\tremoved")

    debug_print('done removing, now adding')
    debug_print(f'LIKED SONGS: {liked_songs}')
    # then go through liked_songs and add each one that's not in sliding tracklist
    for song in liked_songs:
        debug_print(f'for track {song["id"]}')
        if song['id'] not in sliding_tracklist:
            spotify.playlist_add_items(sliding_playlist_id, [ song['id'] ])
            debug_print('\tadded')

def update_main():
    # get config
    config = read_config()

    # auth with spotify
    spotify = get_spotify(config)

    # get tracklist for sliding by least recent
    sliding_tracklist, sliding_playlist_id = get_tracklist(config, spotify, config["SPOTIFY_SLIDING_PLAYLIST"])

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
