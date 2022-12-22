# debug flag
debug = False

def debug_print(*args, **kwargs):
    if debug:
        print(*args, **kwargs) 