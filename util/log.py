import os
import json

from util.date import get_date
from util.config import get_absolute_spotify_repo_path

def truncate_utf8_chars(filename, count, ignore_newlines=True):
    """
    Yoinked from Stack Overflow. - MJ

    Truncates last `count` characters of a text file encoded in UTF-8.
    :param filename: The path to the text file to read
    :param count: Number of UTF-8 characters to remove from the end of the file
    :param ignore_newlines: Set to true, if the newline character at the end of the file should be ignored
    """
    with open(filename, 'rb+') as f:
        size = os.fstat(f.fileno()).st_size

        offset = 1
        chars = 0
        while offset <= size:
            f.seek(-offset, os.SEEK_END)
            b = ord(f.read(1))

            if ignore_newlines:
                if b == 0x0D or b == 0x0A:
                    offset += 1
                    continue

            if b & 0b10000000 == 0 or b & 0b11000000 == 0b11000000:
                # This is the first byte of a UTF8 character
                chars += 1
                if chars == count:
                    # When `count` number of characters have been found, move current position back
                    # with one byte (to include the byte just checked) and truncate the file
                    f.seek(-1, os.SEEK_CUR)
                    f.truncate()
                    return
            offset += 1

def append_to_log(config, removed, added, logfilepath=""):
    if logfilepath == "":
        logfilepath = get_absolute_spotify_repo_path() + config["DATA_DIR"] + config["LOG_FILENAME"]
    # no appending needed if no tracks were removed
    if len(removed) == 0:
        return False

    # add diff to logfile
    with open(logfilepath, "a") as logfile:
        # remove the trailing ] character first
        truncate_utf8_chars(logfilepath, 1)

        changelog = {
            "date": get_date(),
            "in": [],
            "out": []
        }
        for rtrack in removed:
            changelog["out"].append(rtrack)
        for atrack in added:
            # playcounts are not necessary for new tracks in log
            # this is what the updated data store is for
            atrack.pop("playcount")
            changelog["in"].append(atrack)
        logfile.write(',\n' + json.dumps(changelog, indent=4))

        # aaaaand now re-add the trailing ] to ensure valid json list
        logfile.write('\n]')

    return True