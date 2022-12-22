# return none if wrong mode
def get_liked_song_max(config):
    liked_songs_config = config["LIKED_SONGS_SLIDING_WINDOW"]
    if "MAINTAIN_NUM_SONGS" in liked_songs_config["UPDATE_RULE"]:
        return liked_songs_config["UPDATE_RULE"]["MAINTAIN_NUM_SONGS"]

    return None

def get_liked_days_max(config):
    liked_songs_config = config["LIKED_SONGS_SLIDING_WINDOW"]
    if "MAINTAIN_NUM_DAYS" in liked_songs_config["UPDATE_RULE"]:
        return liked_songs_config["UPDATE_RULE"]["MAINTAIN_NUM_DAYS"]

    return None
