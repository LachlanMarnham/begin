import argparse

# from begin.constants import DEFAULT_REGISTRY_NAME


parser = argparse.ArgumentParser(description='A utility for running targets in a targets.py file.')

# parser.add_argument(
#     'target',
#     help='The name of the target to run.',
# )
# parser.add_argument(
#     '-n',
#     '--namespace',
#     default=DEFAULT_REGISTRY_NAME,
#     help='The name of the Registry the target is registered with.',
# )

parser.add_argument(
    '-e',
    '--extension',
    default='*targets.py',
    help='The suffix to match target file patterns against.',
)

parser.add_argument(
    '-g',
    '--global-dir',
    default='home',
    help='The location of the directory holding global targets files.',
)
parsed_args = parser.parse_args()

print(parsed_args)

import pdb; pdb.set_trace()
print(parsed_args, parser)