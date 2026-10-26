#!/usr/bin/env python3

import re
import sys
import os
import pexpect
import logging
import argparse
import time
from .comptest import CompletionRunner

# NOTE: I learned how pexpect works and how to use it from a mix of experimentation
# and looking at the code of 'test/t/conftest.py' from the the bash-completion
# repository https://github.com/scop/bash-completion.  Credit where credit is
# due, here are the most important things I learned from that repo:
# - How to change completion settings to work best with pexpect which is the
#   _setup_readline() function here and is 'test/config/inputrc' in bash-completion
# - The right sequence of sending and expecting to get just the output that I
#   want.  However, it is more useful to set a log file in pexpect.spawn() and
#   to 'tail -f' that log file in a separate shell.  Both are useful, I would
#   never have known that I needed to expect '\r's if I was just looking at the
#   log file, but the log file is necessary otherwise I wouldn't have understood
#   what I was doing.
# - Getting the exit codes of commands.  If I had wanted to, I wouldn't have
#   needed their help to do it, but they gave me the idea to want to.
# - Setting wide dimensions.
# I didn't copy them either so it's normal that my thing is different but here
# are some differences that are good to know about
# - They sset a lot of things to ensure that completion picks up the stuff from
#   the bash-completion repo itself rather than what's on the system.  I want
#   to be as close to the system as possible so I don't do that.
# Some questions that I have about how bash-completion does things:
# - They use '@/' as PS1.  I'm not sure why they don't have a more crazy PS1
#   but I guess it never ever occurs naturally.
# - They also define a MAGIC_MARK (and MAGIC_MARK2).  It's used in the function
#   assert_complete.  It looks like when they send most commands, they do
#   bash.sendline(cmd), bash.expect_exact(cmd [+/r/n]), bash.expect_exact(PS1)
#   then the same thing with cmd='echo $?' to get the exit code, but when it
#   comes time to test the actual completion, if the completion produces a
#   single result, BASH won't print another PS1, so what they do is
#   - bash.send(cmd + '\t')  this prints either one completion or many (we don't
#     know which one.
#   - bash.send(MAGIC_MARK) so now we either have
#   /@ <CMD-TO-TEST><REST-OF-SINGLE-COMPLETION><MAGIC_MARK>
#   so if we expect '/@ <CMD-TO-TEST>', then we expect <MAGIC_MARK> then
#   bash.before will be exactly <REST-OF-SINGLE-COMPLETION>.

def get_args():
    # for x in p._actions: print(y.extend(x.option_strings))
    p = argparse.ArgumentParser()
    p.add_argument("--init-files", "-f", metavar='FILE', nargs='*', default=[], help="Files to source before attempting completion")
    p.add_argument("--bash-command", help="Bash command (default 'bash --norc')")
    p.add_argument("-d", metavar='DIRECTORY', help="Working directory to be in")
    p.add_argument("cmd", metavar='CMD', help="Command to complete")
    p.add_argument("--debug", action='store_true')
    p.add_argument("--load-bash-completion", "-l", action='store_true', help="Load BASH completion from likely directories")
    p.add_argument("--log-file", help="Log file")
    p.add_argument("--xtrace-log", help="Log file for xtrace output", default=os.path.expanduser("~/.log.txt"))
    p.add_argument("-x", action="store_true", help="Activate xtrace (set -x)")
    p.add_argument("--verbose-ps4", action='store_true', help="Set verbose PS4.  Only useful if -x option is used")
    p.add_argument("--interact", action='store_true')
    p.add_argument("--color", choices=['red', 'green', 'blue'])
    p.add_argument("--generate-completion", action='store_true', help="Generate completion for this script")
    if 'GENERATE_COMPLETION' in os.environ:
        import compgen
        compgen.completion_from_parser(p, 'compget', ['compget'])
        sys.exit(0)
    return p.parse_args()

def find_bash_completion():
    candidates = [
        '/opt/homebrew/share/bash-completion/bash_completion',
        '/usr/local/share/bash-completion/bash_completion',
        '/usr/share/bash-completion/bash_completion'
    ]
    for f in candidates:
        if os.path.exists(f):
            return f
    logging.error("Could none of the bash completion file candidates exist")

def main():
    args = get_args()
    if args.generate_completion:
        form_autocomplete(get_parser(), "compget")
        return
    init_commands = []
    if args.load_bash_completion:
        bash_comp = find_bash_completion()
        if bash_comp:
            args.init_files = [bash_comp, *args.init_files]
        else:
            print(f"ERROR: Loading bash completion requested but it was not found")
            return 1

    logging.basicConfig(
        format="[{levelname} - {funcName}] {message}",
        style='{',
        level=(logging.DEBUG if args.debug else logging.INFO)
    )

    comp = CompletionRunner(
        bash_command=args.bash_command,
        PS4=('+ ' if not args.verbose_ps4 else
             '+ \033[35m${BASH_SOURCE[0]:-}\033[36m:\033[1;37m${FUNCNAME:-}\033[22;36m:\033[32m${LINENO:-x}\033[36m:\033[0m '),
        init_files=args.init_files,
        init_commands=init_commands,
        directory=args.d,
        logfile=args.log_file,
        xtrace=args.x,
        xtrace_log=args.xtrace_log
    )

    results = comp.get_comp(args.cmd, timeout=1)

    if args.interact:
        comp.bash.sendintr()
        set_ps1="PS1='[comptest shell] $ '"
        comp.bash.send(f"{set_ps1}\n")
        comp.bash.expect_exact(set_ps1)
        comp.bash.interact()

    comp.close()

    if isinstance(results, list):
        print('\n'.join(sorted(results)))
    elif isinstance(results, str):
        print(results)
    else:
        print("No Results", file=sys.stderr)

