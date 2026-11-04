#!/usr/bin/env python3
""" Cook some food """
import argparse
import sys
import os
import logging

def get_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--debug", "-d", action='store_true', help="Turn on debug logging")
    p.add_argument("-F", help="Config file")
    sp = p.add_subparsers()

    p_cook = sp.add_parser("cook", help="Cook food")
    p_cook.add_argument("--vessel", "-v", choices=['pan', 'pot'], help="The vessel to cook in")
    p_cook.add_argument("--temp", "-t", choices=['high', 'medium', 'low'], help="Temperature to cook at")
    p_cook.add_argument("--bowl", "-b", choices=['large', 'small'], help="The bowl to empty into the cooking vessel")

    p_prep = sp.add_parser("prep", help="Prep food")
    p_prep.add_argument("--bowl", "-b", choices=['large', 'small'], help="The bowl to put prepped vegetables into")
    p_prep.add_argument("--vegetable", "-v", choices=['onion', 'carrot', 'potato'], help="The vegetable to prep")

    if os.environ.get('GENERATE_COMPLETION',''):
        import compgen
        compgen.completion_from_parser(p, 'chef', ['chef'], with_descriptions=True)
        sys.exit(0)

    if os.environ.get('COMPLETION_ANALYSIS', ''):
        import compgen
        compgen.analyze(p)

    return p

def get_args():
    return get_parser().parse_args()

def main():
    args = get_args()
    print(args)

if __name__ == "__main__":
    if sys.stderr.isatty():
        logging.addLevelName( logging.WARNING, "\033[0;33m%s\033[0m" % logging.getLevelName(logging.WARNING))
        logging.addLevelName( logging.ERROR,   "\033[0;31m%s\033[0m" % logging.getLevelName(logging.ERROR))
        logging.addLevelName( logging.INFO,    "\033[0;35m%s\033[0m" % logging.getLevelName(logging.INFO))
        logging.addLevelName( logging.DEBUG,   "\033[0;36m%s\033[0m" % logging.getLevelName(logging.DEBUG))

    logger = logging.getLogger(__name__)
    FORMAT = "[TODO {levelname}] {message}"
    logging.basicConfig(format=FORMAT, style='{')
    logger.setLevel(logging.INFO)

    sys.exit(main())
