from spotipy import CacheHandler

from util.config import write_config, read_config

class ConfigCacheHandler(CacheHandler):
    """
    Handles reading and writing cached Spotify authorization tokens
    by appending them to the config JSON file.
    """

    def get_cached_token(self):
        config = read_config()
        return config.get("SPOTIFY_TOKEN", None)

    def save_token_to_cache(self, token_info):
        config = read_config()
        config["SPOTIFY_TOKEN"] = token_info
        write_config(config)