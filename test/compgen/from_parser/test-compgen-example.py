import os
import sys
import subprocess

this_dir=os.path.dirname(os.path.realpath(__file__))
root = os.path.normpath(os.path.join(this_dir, '..','..','..'))
pack_dir = os.path.join(root, 'src', 'python')

# To import comptest in this file
sys.path.append(pack_dir)

# To import compgen in compgen-example.py
pythonpath = os.environ.get('PYTHONPATH', '')
os.environ['PYTHONPATH'] = f'{pack_dir}:{pythonpath}' if pythonpath else pack_dir

# To have the file lazy-loaded by bash-completion
compdir = os.path.join(this_dir, 'share', 'bash-completion', 'completions')
os.makedirs(compdir, exist_ok=True)
compfile = os.path.join(compdir, '_echo-server')
os.environ['XDG_DATA_DIRS'] = os.path.join(this_dir, 'share')

#
# Call our tool with the --autocomplete flag
#
import comptest
with open(compfile, 'w') as f:
    subprocess.run([f'{this_dir}/compgen-example.py', '--autocomplete'], stdout=f)


bash_comp = comptest.find_bash_completion()

c = comptest.CompletionRunner(
    init_files=[bash_comp],
    xtrace=True,
    logfile="termoutput"
)

results=[]
def test(cmd, expected, timeout=None):
    comp = c.get_comp_magic(cmd, timeout=timeout)
    if isinstance(comp, list):
        passed = set(expected) == set(comp)
    elif isinstance(comp, str):
        passed = comp == expected
    elif comp is None:
        passed = expected is None
    if not passed:
        print(f"Completion for '{cmd}' failed: expected '{expected}', got '{comp}'")
        sys.exit(1)

test('echo-server ', [
    '--allowed-origins', '--autocomplete', '--cert', '--color', '--curl-notes',
    '--debug', '--forward', '--help', '--host', '--key', '--port', '-c', '-h', '-p'
    ]
)
test('echo-server --color ', ['red', 'green', 'blue'])
