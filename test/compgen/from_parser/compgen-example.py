#!/usr/bin/env python3

import compgen
import argparse
import sys

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--color", "-c", choices=['red', 'green', 'blue'])
    p.add_argument("--port", "-p", type=int, help="Port to listen on", default=5447)
    p.add_argument("--host", help="Host to listen on", default="0.0.0.0")
    p.add_argument("--curl-notes", action='store_true', help="Print curl notes and exit")
    p.add_argument("--forward", help="Address to forward request to")
    p.add_argument("--allowed-origins", help="Comma separated list of allowed origins")
    p.add_argument("--debug", action='store_true')
    p.add_argument("--cert")
    p.add_argument("--key")
    p.add_argument("--autocomplete", action='store_true', help="Generate autocomplete code and exit")

    args = p.parse_args()
    if args.autocomplete:
        compgen.CompletionGenerator(parser=p, namespace='echo_server', commands=['echo-server']).generate()
        sys.exit(0)

    return args

def main():
    args = get_args()

if __name__ == "__main__":
    sys.exit(main())
