import argparse


p = argparse.ArgumentParser()

p.add_argument('--dressing', '-d', choices=['italian', 'ranch'])
p.add_argument('--seasoning', '-s', nargs='+', choices=['salt', 'pepper'])
p.add_argument('--vegetable', '-v', nargs='*', choices=['celery', 'carrot', 'broccoli', 'potato'])
p.add_argument('--fruit', '-f', nargs=3, choices=['apple', 'apricot', 'banana', 'cherry'])


import compgen

compgen.completion_from_parser(p, namespace='salad', commands=['salad'], advanced=True)
