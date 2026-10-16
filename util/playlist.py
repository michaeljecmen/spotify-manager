import html

from spotipy import SpotifyException

from util.debug import debug_print


def find_playlist(spotify, playlist_owner_username, playlist_name):
    playlists = spotify.user_playlists(playlist_owner_username)
    for playlist in playlists['items']:
        # defense against taking another user's playlist with the same name that 
        # you have liked not sure if this is even possible but why not
        if playlist['owner']['id'] != playlist_owner_username:
            continue

        if playlist['name'] == playlist_name:
            return playlist
    
    return None


# spotify caps how many times one playlist can ever be edited (950,000).
# past that, every add or remove fails with this message
def is_max_change_count_error(e):
    return isinstance(e, SpotifyException) and "maximum change count" in str(e)


def get_all_track_uris(spotify, playlist_id):
    uris = []
    TRACKS_PER_PAGE = 100
    page = spotify.playlist_items(playlist_id, limit=TRACKS_PER_PAGE, offset=0, fields="items(track(uri))")
    while page and page['items']:
        uris.extend([ item['track']['uri'] for item in page['items'] if item['track'] ])
        page = spotify.playlist_items(playlist_id, limit=TRACKS_PER_PAGE, offset=len(uris), fields="items(track(uri))")
    return uris


def add_tracks_in_batches(spotify, playlist_id, uris):
    # the api takes at most 100 tracks per call
    for i in range(0, len(uris), 100):
        spotify.playlist_add_items(playlist_id, uris[i:i+100])


def rotate_playlist(spotify, username, playlist_id):
    """
    Replaces a playlist that has hit spotify's edit cap with a fresh copy:
    same name, description, visibility and tracks in the same order. The old one
    is removed from your library (recoverable for 90 days at spotify.com/account/recover-playlists).
    Since every job finds its playlist by name, no config changes are needed.
    Returns the new playlist's id.
    """
    old = spotify.playlist(playlist_id, fields="name,description,public,collaborative")
    uris = get_all_track_uris(spotify, playlist_id)

    new = spotify.user_playlist_create(
        username,
        old['name'],
        public=bool(old['public']),
        collaborative=bool(old['collaborative']),
        description=html.unescape(old['description'] or ""),
    )
    add_tracks_in_batches(spotify, new['id'], uris)

    # only drop the old playlist once the copy holds every track
    if len(get_all_track_uris(spotify, new['id'])) != len(uris):
        raise RuntimeError(f"rotating playlist {old['name']}: copy is missing tracks, old playlist kept")
    spotify.current_user_unfollow_playlist(playlist_id)

    debug_print(f"rotated playlist {old['name']}: {playlist_id} -> {new['id']}, {len(uris)} tracks")
    return new['id']
