import json
from os.path import dirname, abspath
from util.debug import debug_print

def get_absolute_spotify_repo_path():
    return dirname(dirname(abspath(__file__))) + "/"

def read_config():
    # IMPORTANT: config.json is the only thing that's .gitignore'd
    # don't put your details in example.json, or a file with any other name
    with open(get_absolute_spotify_repo_path() + "config/config.json", "r") as cfile:
        config = json.load(cfile)

    # get required fields from the example file
    with open(get_absolute_spotify_repo_path() + "config/example.json", "r") as example_conf:
        required_fields = json.load(example_conf).keys()

    error = False
    error_msg = ''
    for field in required_fields:
        if field not in config.keys():
            error = True
            error_msg += f'\"{field}\", '
    
    if error:
        debug_print('ERROR: your config.json is missing the following required fields:')
        debug_print('\t[ ', end='')
        error_msg = error_msg[:-2] # pop trailing comma and space
        debug_print(error_msg, end='')
        debug_print(' ]')
        exit(1)

    return config

def write_config(config):
    with open(get_absolute_spotify_repo_path() + "config/config.json", "w") as cfile:
        json.dump(config, cfile, indent=4)

# return none if wrong mode
def get_liked_song_max(config):
    if "MAINTAIN_NUM_SONGS" in config["UPDATE_RULE"]:
        return config["UPDATE_RULE"]["MAINTAIN_NUM_SONGS"]

    return None

def get_liked_days_max(config):
    if "MAINTAIN_NUM_DAYS" in config["UPDATE_RULE"]:
        return config["UPDATE_RULE"]["MAINTAIN_NUM_DAYS"]

    return None
