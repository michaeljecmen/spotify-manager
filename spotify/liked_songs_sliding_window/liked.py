from datetime import datetime
from util.debug import debug_print

# return list of previous n liked songs, sorted with newest first
def get_previous_n_liked_songs(spotify, n):
    liked = []
    while len(liked) < n:
        # offset by number of songs we've already gathered
        resp = spotify.current_user_saved_tracks(offset=len(liked))
        liked.extend([ track['track']['id'] for track in resp['items'] ])
    
    # chop at n exactly
    return liked[:n]

# song is dict of {id, added_at}
def was_added_within_n_days(song, n):
    ts = datetime.strptime(song['added_at'], "%Y-%m-%dT%H:%M:%SZ")
    diff = datetime.now() - ts
    return diff.days <= n

def get_all_liked_songs_within_last_n_days(spotify, n):
    liked = []
    while len(liked) == 0 or was_added_within_n_days(liked[-1], n):
        # offset by number of songs we've already gathered
        resp = spotify.current_user_saved_tracks(offset=len(liked))
        liked.extend([ {"id":track['track']['id'], "added_at":track['added_at']} for track in resp['items'] ])

    debug_print(f'LIKED: {liked}')
    # now chop everything not within last n days
    while len(liked) > 0 and not was_added_within_n_days(liked[-1], n):
        debug_print(f'{liked[-1]["added_at"]} is not within last {n} days')
        liked.pop()

    # liked = [ track for track in liked where track['track']]
    # i wonder for what n, k bsearch would start outperforming
    # a linear search from the back. k being default num returned
    # tracks from current_user_saved_tracks

    return liked