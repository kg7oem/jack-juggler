#/usr/bin/env python3

# Thank you https://stormpath.com/blog/building-simple-cli-interfaces-in-python !

from os.path import abspath, dirname, join
from setuptools import Command, find_packages, setup
from subprocess import call

from jack_juggler import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=skele', '--cov-report=term-missing'])
        raise SystemExit(errno)

setup(
    name = 'jack-juggler',
    version = __version__,
    description = 'Manages JackAudio client connections',
    long_description = long_description,
    url = 'https://github.com/kg7oem/jack-juggler',
    author = 'Tyler Riddle',
    author_email = 'cardboardaardvark@gmail.com',
    license = 'GPL3',
    classifiers = [
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    keywords = 'cli',
    packages = find_packages(exclude=['docs', 'tests*']),
    # install_requires = ['docopt'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points = {
        'console_scripts': [
            'jack-juggler=jack_juggler:main',
        ],
    },
    cmdclass = {'test': RunTests},
)
