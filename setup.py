import os
from setuptools import setup

def recursive(paths, rel='.'):
    l = []
    for path in paths:
        for x, y, z in os.walk(os.path.join(rel, path)):
            if z:
                l.append(os.path.relpath(os.path.join(x, '*'), rel))
    return l

setup(
    name='qwe-client',
    version='0.0.1',
    description='QPython Web Editor command line client',
    author='cdtx',
    classifiers=[
        'Programming Language :: Python :: 2',
    ],
    packages=['cdtx.qwe-client'],
)



