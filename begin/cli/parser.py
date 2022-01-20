import argparse


parser = argparse.ArgumentParser()

parser.add_argument(
    'target',
    help='The name of the target to run.',
)
parser.add_argument(
    '-n',
    '--namespace',
    default='default',
    help='The name of the Registry the target is registered with.',
)

args = parser.parse_args()

print(args.target, args.namespace)
