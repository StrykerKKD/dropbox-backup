from setuptools import setup

setup(
    name='dropboxbackup',
    version='0.1',
    py_modules=['dropboxbackup'],
    install_requires=[
        'click',
        'dropbox',
        'simple-crypt'
    ],
    entry_points='''
        [console_scripts]
        dropboxbackup=dropboxbackup:cli
    ''',
)
