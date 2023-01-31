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