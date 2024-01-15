from spotify.liked_songs_sliding_window.util.update_rule import get_liked_song_max, get_liked_days_max

from util.config import read_config
from util.spotify import get_spotify
from spotify.liked_songs_sliding_window.liked import get_previous_n_liked_songs, get_all_liked_songs_within_last_n_days
from util.debug import debug_print
from util.gmail import debug_print_and_email_message

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

def fetch_full_tracklist(spotify, playlist):
    tracklist = {}

    # because next no longer works, we have to use playlist_items
    # instead of this
    # results = spotify.playlist(playlist['id'], fields="tracks,next")
    current_track_offset = 0
    TRACKS_PER_PAGE = 100
    spotify_tracks = spotify.playlist_items(playlist['id'], limit=TRACKS_PER_PAGE, offset=current_track_offset)

    while spotify_tracks and spotify_tracks['items']:
        # not quite sure why the for loop is needed here
        for item in spotify_tracks['items']:
            spotify_track = item['track']
            debug_print("fetch_full_tracklist: found track!", spotify_track['name'])
            tracklist[spotify_track['uri']] = {
                "name": spotify_track['name'],
                "artists": [ artist['name'] for artist in spotify_track['artists'] ],
                "album": spotify_track['album']['name'],
                "uri": spotify_track['uri'],
            }

        # as of jan 2024 spotify.next no longer works. neat
        # spotify_tracks = spotify.next(spotify_tracks)
        
        # now we have to do the math ourselves
        current_track_offset += TRACKS_PER_PAGE
        spotify_tracks = spotify.playlist_items(playlist['id'], limit=TRACKS_PER_PAGE, offset=current_track_offset)
    
    debug_print("fetch_full_tracklist returning:", tracklist)
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

def update_liked_songs_playlist(config: dict) -> None:
    # get config
    config = read_config()

    # auth with spotify
    spotify = get_spotify(config)

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
    except Exception as e:
        # debug_print_and_email_message(config, "error in liked-songs-sliding-window", str(e))
        pass
