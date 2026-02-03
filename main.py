import src.housey_logging
src.housey_logging.configure()

import sys
import src.twitch_dj_clipper
import logging

def main():
    logging.info("starting twitch_dj_clipper twitch chatbot")
    logging.info("only errors will be displayed unless otherwise configured")
    src.twitch_dj_clipper.main()


if __name__ == "__main__":
    sys.excepthook = src.housey_logging.log_exception

    main()
