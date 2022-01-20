import argparse
from begin.constants import DEFAULT_REGISTRY_NAME

parser = argparse.ArgumentParser()

parser.add_argument(
    'target',
    help='The name of the target to run.',
)
parser.add_argument(
    '-n',
    '--namespace',
    default=DEFAULT_REGISTRY_NAME,
    help='The name of the Registry the target is registered with.',
)

args = parser.parse_args()

print(args.target, args.namespace)
