#!/usr/bin/env python3
""" Cook some food """
import argparse
import sys
import logging

def get_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--debug", action='store_true', help="Turn on debug logging")
    p.add_argument("-F", help="Config file")
    sp = p.add_subparsers()

    p_cook = sp.add_parser("cook", help="Cook food")
    p_cook.add_argument("--vessel", choices=['pan', 'pot'])
    p_cook.add_argument("--temp", choices=['high', 'medium', 'low'])
    p_cook.add_argument("--bowl", choices=['large', 'small'])

    p_prep = sp.add_parser("prep", help="Prep food")
    p_prep.add_argument("--bowl", choices=['large', 'small'])
    p_prep.add_argument("--vegetable", choices=['onion', 'carrot', 'potato'])
    analyze(p)

    return p.parse_args()

def analyze(p: argparse.ArgumentParser, test=False):
    tests = []
    base_actions = []
    subparser_action = None
    for a in p._actions:
        if isinstance(a, argparse._SubParsersAction):
            subparser_action = a
        else:
            base_actions.append(a)

    if subparser_action:
        print(f"Toplevel options")
        base_option_strings = []
        for a in base_actions:
            base_option_strings.extend(a.option_strings)
            print(f"    {a.option_strings}: {a.help}")

        subcommands = list(subparser_action.choices.keys())

        tests.append(f"test('chef ', {[*subcommands, *base_option_strings]})")
        for subcommand, sp in subparser_action.choices.items():
            print(f"    {subcommand}")
            arguments = []
            for a in sp._actions:
                print(f"        {a.option_strings}: {a.choices or ''} {a.help}")
                arguments.extend(a.option_strings)
                if a.choices:
                    for os in a.option_strings:
                        tests.append(f"test('chef {subcommand} {os} ', {a.choices})")
            tests.append(f"test('chef {subcommand} ', {arguments})")

    for t in tests:
        print(t)

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
