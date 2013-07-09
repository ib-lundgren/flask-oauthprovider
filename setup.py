# -*- coding: utf-8 -*-

from os.path import dirname, join
from setuptools import setup, find_packages


def fread(fn):
    with open(join(dirname(__file__), fn), 'r') as f:
        return f.read()

tests_require = ['nose', 'unittest2']

requires = ['oauthlib<=0.5.0']

setup(
    name='flask-oauthprovider',
    version='0.1.3',
    description='A full featured and secure OAuth provider base',
    long_description=fread('README.rst'),
    author='Ib Lundgren',
    author_email='ib.lundgren@gmail.com',
    url='https://github.com/ib-lundgren/flask-oauthprovider',
    license=fread('LICENSE'),
    py_modules=['flask_oauthprovider'],
    test_suite='nose.collector',
    tests_require=tests_require,
    extras_require={'test': tests_require},
    install_requires=requires,
    zip_safe=False,
    include_package_data=True,
)
