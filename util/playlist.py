def find_playlist(config, spotify, playlist_name):
    # get sliding playlist id
    spotify_username = config["SPOTIFY_USERNAME"]
    playlists = spotify.user_playlists(spotify_username)
    for playlist in playlists['items']:
        # defense against taking another user's playlist with the same name that 
        # you have liked not sure if this is even possible but why not
        if playlist['owner']['id'] != spotify_username:
            continue

        if playlist['name'] == playlist_name:
            return playlist
    
    return None