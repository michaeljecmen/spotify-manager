from spotify.monthly_recap.monthly import main
from util.debug import set_debug

import sys

if __name__ == '__main__':
    # debug printing on for any invocation with more than the required args
    set_debug(len(sys.argv) > 1)
    main()
