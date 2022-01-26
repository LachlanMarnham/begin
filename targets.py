from begin import Registry
from begin.recipes import (
    flake8,
    pytest,
)


registry = Registry()


@registry.register_target
def check_style():
    flake8()


@registry.register_target
def tests():
    pytest('--cov', 'begin')


# TODO change recipe name to tests
@registry.register_target
def tests_coverage():
    import sysconfig
    import sys
    import os
    pth_dir = sysconfig.get_path("purelib")
    pth_path = os.path.join(pth_dir, "zzz_setup.cfg")
    with open(pth_path, "w") as pth_file:
        pth_file.write("import coverage; coverage.process_startup()\n")

    import coverage
    cov = coverage.Coverage(config_file="setup.cfg")
    cov._warn_unimported_source = False
    cov._warn_preimported_source = False
    cov.start()

    import begin
    covmods = {}
    begin_dir = os.path.split(begin.__file__)[0]

    # We have to make a list since we'll be deleting in the loop.
    modules = list(sys.modules.items())
    for name, mod in modules:
        if name.startswith('begin'):
            if getattr(mod, '__file__', "??").startswith(begin_dir):
                covmods[name] = mod
                del sys.modules[name]
    import coverage                         # pylint: disable=reimported
    # sys.modules.update(covmods)

    # Run tests, with the arguments from our command line.
    pytest('--cov', 'begin')

    cov.stop()
    os.remove(pth_path)
    cov.combine()
    cov.save()
    import pdb; pdb.set_trace()
    print(pth_path)


@registry.register_target
def install():
    print('default install')
