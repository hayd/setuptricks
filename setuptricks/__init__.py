"""setuptricks, useful utilities for setup.py."""

from ast import parse
import os
from subprocess import Popen
import sys


def before_setup(package, file_with_version=None):
    """Call this before setuptools.setup in setup.py."""
    if sys.argv[-1] == 'publish':
        publish()
        print("You probably want to also tag the version now:")
        print("  python setup.py tag.")
        sys.exit(0)
    elif sys.argv[-1] == 'tag':
        tag(package, file_with_version)
        sys.exit(0)

# to pass to setup
def description(package):
    """Return module docstring used in the package __init__.py."""
    return _get_module_docstring(_package_init(package))

def get_packages(package):
    """Return root package and all sub-packages."""
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]

def get_package_data(package):
    """Return all files under the root package, that are not in a package
    themselves.
    """
    # TODO excludes?
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

def md_readme_as_rst(readme="README.md"):
    """Read README.md as an rst."""
    try:
        import pypandoc
        return pypandoc.convert(readme, 'rst', format='md')
    except (IOError, ImportError):
        # if it fails then just read the markdown as rst...
        # potentially we should just raise here?
        with open('README.md') as f:
            return f.read()

def version(package, file_with_version=None):
    """Return version string."""
    if file_with_version is None:
        file_with_version = _package_init(package)

    with open(file_with_version) as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return parse(line).body[0].value.s

    raise LookupError("__version__ not found in file_with_version.")

def _get_module_docstring(filepath):
    """Get module-level docstring of Python module at filepath."""
    # https://gist.github.com/rduplain/1249199
    co = compile(open(filepath).read(), filepath, 'exec')
    if co.co_consts and isinstance(co.co_consts[0], str):
        docstring = co.co_consts[0]
    else:
        docstring = ""
    return docstring

def _package_init(package):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        package,
                        '__init__.py')

# cli api
def publish():
    Popen("python setup.py sdist upload".split())
    # TODO Perhaps wheel should be optional?
    Popen("python setup.py bdist_wheel upload".split())

def tag(package, file_with_version=None):
    v = version(package, file_with_version)
    Popen(["git", "tag", "-a", v, "-m", "bump version to %s" % v]).wait()
    Popen(["git", "push", "--tags"]).wait()

