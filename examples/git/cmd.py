
#!/usr/bin/env python3
""" Cook some food """
import argparse
import sys
import os
import logging

def get_args():
    p = argparse.ArgumentParser(prog='git', description=__doc__)
    p.add_argument("--debug", "-d", action='store_true', help="Turn on debug logging")
    p.add_argument("-F", choices=['main-F', 'x'], help="Config file")
    sp = p.add_subparsers()

    push = sp.add_parser("push", help="push refs to remotes")
    push.add_argument("remote", choices=['upstream', 'origin'])
    push.add_argument("ref", choices=['main', 'dev'])
    push.add_argument("--color", nargs=2, choices=['magenta', 'cyan', 'yellow'])
    push.add_argument("--all", action='store_true', help="flag option")
    push.add_argument("--random", nargs="*", help='Random nargs * option')

    remote = sp.add_parser("remote", help="Do remote stuff")
    remote_sp = remote.add_subparsers()

    remote_add = remote_sp.add_parser("add", help="add a remote")
    remote_add.add_argument("--name", choices=['remote-add--name', 'origin', 'upstream'])

    remote_remove = remote_sp.add_parser("remove", help="Remove a remote")
    remote_remove.add_argument("--name", nargs=3, help="Remove an existing remote", choices=['remote-remove--name', 'x'])
    remote_remove.add_argument("--force", help="Remove even if something", choices=['remote-remove--force', 'x'])


    worktree = sp.add_parser("worktree", help="worktree stuff")
    worktree_sp = worktree.add_subparsers()

    worktree_add = worktree_sp.add_parser("add", help="Add a worktree")
    worktree_add.add_argument("--name", choices=['worktree-add--name', 'x'])

    worktree_del = worktree_sp.add_parser("delete", help="Add a worktree")
    worktree_del.add_argument("--name", choices=['worktree-delete--name', 'x'])

    if os.environ.get('GENERATE_COMPLETION',''):
        import compgen
        compgen.completion_from_parser(p, 'git', ['git', 'g'], with_functions=True, with_descriptions=True, advanced=True)
        sys.exit(0)

    if os.environ.get('COMPLETION_ANALYSIS', ''):
        import compgen
        compgen.analyze(p)
        sys.exit(0)

    return p.parse_args()

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
