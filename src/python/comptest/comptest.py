#!/usr/bin/env python3

import sys
import os
import pexpect
import logging
import argparse
import time

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--init-files", "-f", metavar='FILE', nargs='*', default=[], help="Files to source before attempting completion")
    p.add_argument("-d", metavar='DIRECTORY', help="Working directory to be in")
    p.add_argument("cmd", metavar='CMD', help="Command to complete")
    p.add_argument("--debug", action='store_true')
    p.add_argument("--load-bash-completion", action='store_true', help="Load BASH completion from likely directories")
    p.add_argument("--log", help="Log file", default=os.path.expanduser("~/.log.txt"))
    p.add_argument("-x", action="store_true", help="Activate xtrace (set -x)")
    return p.parse_args()

def main():
    args = get_args()
    init_files=[]
    if args.load_bash_completion:
        candidates = [
                '/opt/homebrew/share/bash-completion/bash_completion',
                '/usr/local/share/bash-completion/bash_completion',
                '/usr/share/bash-completion/bash_completion'
        ]
        for f in candidates:
            if os.path.exists(f):
                args.init_files.append(f)
                break
        else:
            print(f"ERROR: Loading bash completion requested but none of {candidates} exist")
            return 1
    if args.x:
        init_commands.append(f"exec {{BASH_XTRACEFD}}>>{args.log}")
        init_commands.append("set -x")

    logging.basicConfig(
        format="[{levelname} - {funcName}] {message}",
        style='{',
        level=(logging.DEBUG if args.debug else logging.INFO)
    )
    comp = CompletionRunner(init_files=args.init_files, directory=args.d)
    results = comp.get_completion_candidates(args.cmd, timeout=1)
    comp.close()
    print('\n'.join(sorted(results)))

class CompletionRunner:
    def __init__(self, PS1="@/", directory=None, init_files=None, init_commands=None, logfile=None):
        self.PS1 = PS1
        env = os.environ.copy()
        env['TERM']='dumb'
        self.bash = pexpect.spawn(
            "bash --norc",
            cwd=(os.path.realpath(directory) if directory else os.getcwd()),
            encoding='utf-8',
            env=env,
            dimensions=(24,240),
            logfile=open(logfile,'a') if logfile else None
        )
        self.running = True
        self.bash.sendline(f"PS1={self.PS1}")
        self.bash.expect_exact(f"PS1={self.PS1}\r\n{self.PS1}")
        if init_files:
            # To load bash_completion and the completion definitions for
            # the command we want to test.
            for f in init_files:
                self.run_command(f"source {f}")
        if init_commands:
            for c in init_commands:
                logging.debug(self.run_command(c))
        self._setup_readline()

    def close(self):
        # When running this with a command that only produces one
        # candidate, this produces an exception (which is extra bad when it
        # happens inside a '__del__' method.  Why does this only happen when
        # the command produces only one candidate?
        self.bash.send("exit")

    def _setup_readline(self):
        # Pagin could prevent us from getting a PS1 after hitting TAB
        self.run_command('bind "set page-completions off"')
        # Don't query when there are lots of completions
        self.run_command('bind "set completion-query-items -1"')
        # Print each completion on its own line
        self.run_command('bind "set completion-display-width 0"')
        # Press TAB once to see all completions
        self.run_command('bind "set show-all-if-ambiguous"')
        # Prevent output from getting polluted with Bell (\a) or ANSI color codes
        self.run_command('bind "set bell-style none"')
        self.run_command('bind "set colored-completion-prefix off"')
        self.run_command('bind "set colored-stats off"')

    def run_command(self, cmd, nl_after_command=True, nl_before_ps1=False):
        logging.debug(f"cmd='{cmd}'")
        self.bash.sendline(cmd)
        self.bash.expect_exact(cmd + ('\r\n' if nl_after_command else ''))
        self.bash.expect_exact(('\r\n' if nl_before_ps1 else '') + self.PS1)
        logging.debug(f"Found ps1 after command '{cmd}'")
        return self.bash.before

    def expect_single_candidate(self, cmd, expected_completion, timeout=None):
        logging.debug(f"sending '{cmd}\\t'")
        self.bash.send(cmd + '\t')
        self.bash.expect_exact(cmd)
        completion = None
        try:
            self.bash.expect_exact(expected_completion, timeout=timeout)
            completion = self.bash.after
        except pexpect.exceptions.TIMEOUT as t:
            logging.debug(f"Timeout reached")
            self.bash.sendintr()
            self.bash.expect_exact(self.PS1)
            return False
        logging.debug(f"before = '{self.bash.before}'")
        if '\n' in self.bash.before:
            logging.warning(f"newline in buffer between command and expected completion indicates more than one candidate either this indicates a failed test or that the test itself should be done with expect_multiple_candidates()")
            self.bash.sendintr()
            self.bash.expect_exact(self.PS1)
            return False
        self.bash.sendintr()
        self.bash.expect_exact(self.PS1)
        logging.debug(f"expected_completion='{expected_completion}'")
        logging.debug(f"completion='{completion}'")
        return expected_completion == completion

    def expect_multiple_candidates(self, cmd, expected_completions, timeout=None):
        result = self.get_completion_candidates(cmd, timeout)
        logging.debug(f"expected - result = {set(expected_completions) - result}")
        return (result == set(expected_completions))

    def get_completion_candidates(self, cmd, timeout=1):
        # NOTE: bash-completion does something with 'MAGIC_MARK' which seems
        # to be some token that is super unlikely to arise in the ouput of
        # a command.
        logging.debug(f"Getting candidates for command {cmd}")
        logging.debug(f"sending '{cmd}\\t'")
        self.bash.send(cmd + "\t")
        logging.debug(f"expect exact: '{cmd}'")
        self.bash.expect_exact(cmd)
        try:
            self.bash.expect_exact(self.PS1, timeout=timeout)
        except pexpect.exceptions.TIMEOUT as t:
            logging.debug(f"Timeout reached")
        result = set(self.bash.before.strip().splitlines())
        self.bash.sendintr()
        self.bash.expect_exact(self.PS1)
        return result

if __name__ == "__main__":
    main()
