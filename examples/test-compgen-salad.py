

import subprocess
import os
this_dir = os.path.dirname(__file__)
sys.path.append(os.path.normpath(os.path.join(this_dir, "..", "src", "python")))


with open("_salad", 'w') as f:
    subprocess.run(['python3', 'salad.py'], stdout=f)


import comptest
bash_comp = comptest.find_bash_completion()
c = comptest.CompletionRunner(init_files=["_salad", bash_comp])

print(c.get_comp('salad --fruit apple '))
print(c.get_comp('salad --fruit apple banana '))
print(c.get_comp('salad --fruit apple banana cherry '))

print(c.get_comp('salad --vegetable celery potato potato potato '))
print(c.get_comp('salad --vegetable celery potato potato potato -'))
