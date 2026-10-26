# Stuff for making and testing completions

## Installation

Clone this repo and run one of these commands from the root of the repo:

```bash
make install
make install-dev
```

With `install-dev`, the installed files will all be links to the files in this
repo.

## Usage

### Generating completions (`compgen`)

In your own program that uses `argparse`, you need to pass the instance of
`argparse.ArgumentParser` that you created to `compgen.completion_from_parser()`
along with a namespace which will be prefixed the global identifiers in the
generated code, and the commands to set this completion for.

```python
import argparse
import compgen
import sys

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument(...)
    p.add_argument(...)

    if 'GENERATE_COMPLETION' in os.environ:
        compgen.completion_from_parser(p, 'my_thing', ['my-thing']
        sys.exit(0)

    return p.parse_args()
```

Any way you choose to trigger a call to the function is good.  In this example
we use the environment variable `GENERATE_COMPLETION` so in this case:
```bash
GENERATE_COMPLETION=1 my-thing > _my-thing
```

### Testing completions and getting candidates programmatically

The `comptest` package uses techniques learned from studying how the
`bash-completion` repo uses a pseudoterminal (PTY) to test their completions.

For both methods, a BASH instance gets created and in that bash instance, a
default setup is done for readline, then, if provided, init files are sourced
init commands are run.

#### Command line tool `compget`

The `compget` command returns the completion candidates obtained when
typing `CMD` and pressing `TAB`.
```bash
compget [OPTIONS...] [--load-bash-completion] [--init-files FILES] -- CMD
```

For example
```
$ compget --init-files ~/.git-completion.bash -- 'git co'
commit
commit-with-blob
comparedir
comparetxt
config
```

Use `--` before `CMD` if you use `--init-files` to make sure that `CMD` is not
used as an init file.

#### Python class `comptest.CompletionRunner`

This is the class used to implement `compget` above.  The class itself can
be used as well to write tests for completions (or anything else you can think
about).

```python
import comptest
c = comtest.CompletionRunner(
    init_files=['git-completion.bash']
)
results = set(c.get_comp('git co'))
expected = set(('commit', 'commit-with-blob', 'comparedir', 'comparetxt', 'config'))
if results != expected:
    print(f"Test failed: expected {expected}, got {results}")
```

