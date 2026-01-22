from src import housey_logging
housey_logging.configure()

import sys
from src import twitch_dj_clipper

def main():
    twitch_dj_clipper.main()


if __name__ == "__main__":
    sys.excepthook = housey_logging.log_exception

    main()
