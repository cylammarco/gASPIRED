"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

import os
import subprocess
import sys
from setuptools import setup

# Get Python path - works in virtualenv, too
python_path = subprocess.Popen([
    "which",
    "python3"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    close_fds=True).communicate()[0].rstrip().decode("utf-8")
# print(python_path)
python_path = os.path.dirname(os.path.dirname(python_path))
django_admin_path = os.path.join(python_path, 'lib', 'python3.7',
                                 'site-packages', 'django', 'contrib', 'admin')


APP = ['main.py']

DATA_FILES = ['pages', 'ASPIRED', 'main.py', 'manage.py', 'OPTICON.icns',
              os.path.join(django_admin_path, 'templates'),
              os.path.join(django_admin_path, 'static'),
              ]

OPTIONS = {'argv_emulation': True,
           'iconfile': './OPTICON.icns',
           'packages': ["django"],
           'includes': ['WebKit', 'Foundation', 'webview',
                        'packaging', 'six', 'packaging.version',
                        'packaging.specifiers', 'packaging.requirements',
                        'requests'],
           'plist': {
                'CFBundleIdentifier': "uk.ac.livjm.telescope",
                'CFBundleName': "ASPIRED",
                'CFBundleVersion': '1001',
                'CFBundleShortVersionString': '1.0',
               'NSHumanReadableCopyright': 'Copyright 2019 Liverpool Telescope'
           }
          }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)

