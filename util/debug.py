DEBUG = False

def set_debug(debug):
    global DEBUG
    DEBUG = debug

def debug_print(*args, **kwargs):
    if not DEBUG:
        return
    print(*args, **kwargs)