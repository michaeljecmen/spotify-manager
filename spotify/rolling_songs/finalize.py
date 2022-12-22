#!/usr/bin/python3

import json
import sys
import shutil

from util.config import read_config, get_absolute_spotify_repo_path
from util.lastfm import get_lastfm_network
from util.log import append_to_log

# takes the current tracklist and appends
# the relevant information to the logfile
# also re-parses and pretty prints the logfile, 
# which has probably been pretty ugly up until now
def finalize(outfilepath):
    config = read_config()
    lastfm = get_lastfm_network(config).get_authenticated_user()

    trackfilename = config["DATA_DIR"] + config["STORAGE_FILENAME"]
    with open(get_absolute_spotify_repo_path() + trackfilename, "r") as trackfile:
        tracklist = json.load(trackfile)
    
    for track in tracklist:
        # update playcounts to be as up-to-date as possible
        scrobs = lastfm.get_track_scrobbles(track["artists"][0], track["name"])
        track["playcount"] = len(scrobs) - track["playcount"]

    # copy the logfile over so we don't lose the original
    shutil.copy(config["DATA_DIR"] + config["LOG_FILENAME"], outfilepath)
    append_to_log(config, tracklist, [], outfilepath)

    # write log to new file prettily
    with open(outfilepath, "r") as outfile:
        json_log = json.load(outfile)
    
    with open(outfilepath, "w") as outfile:
        json.dump(json_log, outfile, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 finalize.py {OUTPUT_FILE_PATH}")
        print("this will overwrite that file if it exists, dumping the json contents of the log into it.")
        exit(1)
    finalize(sys.argv[1])

    # TODO mj
    # export file to web server dir
    # start script to generate webpage and allow it to be served (different repo)
    # then make this finalize script auto-run once per year (dec 31 after rolling script)