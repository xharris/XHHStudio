'''
from setuptools import setup,find_packages
import sys
import ez_setup
ez_setup.use_setuptools()

APP = ['main.py']
OPTIONS = {'argv_emulation': True}
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

'''
# An example setup.py that can be used to create both standalone Windows
# executables (requires py2exe) and Mac OS X applications (requires py2app).
#
# On Windows::
#
#     python setup.py py2exe
#
# On Mac OS X::
#
#     python setup.py py2app
#

from distutils.core import setup

import os,shutil

# The main entry point of the program
script_file = 'main.py'
data_folder = 'DATA'
icon_location = 'DATA/icon.ico'

# Setup args that apply to all setups, including ordinary distutils.
setup_args = dict(
    zipfile=None,
    options={
        "py2exe":{
            'compressed':1,
            'optimize':2,
            'bundle_files':1,
            "dll_excludes":["w9xpopen.exe","tcl85.dll", "tk85.dll"],
            }}
)

# py2exe options
try:
    import py2exe
    setup_args.update(dict(
        windows=[dict(
            script=script_file,
            icon_resources=[(1,icon_location)],
        )]
    ))
except ImportError:
    pass


# py2app options
try:
    import py2app
    setup_args.update(dict(
        app=[script_file],
        options=dict(py2app=dict(
            argv_emulation=True#,
            #iconfile='assets/app.icns',
        )),
    ))
except ImportError:
    pass


setup(**setup_args)