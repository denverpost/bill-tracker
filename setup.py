#!/usr/bin/env python
from setuptools import setup, Command
import subprocess


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['python -m py.test'])
        raise SystemExit(errno)

setup(
    name='BillTracker',
    version='0.1',
    description='Track Colorado State bills',
    license='Apache',
    url='https://github.com/denverpost/bill-tracker',
    author='The Denver Post',
    author_email='dpo@denverpost.com',
    packages=['bill-tracker'],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    )
