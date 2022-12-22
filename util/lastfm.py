import pylast

def get_lastfm_network(config):
    network = pylast.LastFMNetwork(
        api_key=config["LASTFM_API_KEY"],
        api_secret=config["LASTFM_SECRET"],
        username=config["LASTFM_USERNAME"],
        password_hash=pylast.md5(config["LASTFM_PASSWORD"])
    )
    return network