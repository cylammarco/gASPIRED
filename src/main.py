# -*- coding: utf-8 -*-

import threading
import webview
import subprocess
import sys
import os
import logging
import logging.handlers

# check if we are running as py2app bundle or as a script
if getattr(sys, 'frozen', None):
    base_dir = os.path.realpath(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    run_as_binary = True
else:
    base_dir = os.path.realpath(os.path.dirname(__file__))
    run_as_binary = False

# set up logging and app_name
if run_as_binary is True:
    log_file = os.path.join(base_dir, "..", "PyBrowse.log")
    cherry_access_log = os.path.join(base_dir, "..", "access.log")
    cherry_error_log = os.path.join(base_dir, "..", "error.log")
    app_name = "PyBrowse"
else:
    log_file = os.path.join(base_dir, "PyBrowse.log")
    cherry_access_log = os.path.join(base_dir, "access.log")
    cherry_error_log = os.path.join(base_dir, "error.log")
    app_name = "Python"

log = logging.getLogger("PyBrowse")
log.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(log_file,
                                               maxBytes=30000000,
                                               backupCount=10)
handler.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(fmt)
log.addHandler(handler)

ip = "127.0.0.1"
port = "9090"

def run_server():
    # code to start your server
    subprocess.Popen(["python3", "manage.py", "runserver", ip + ":" + port])

t = threading.Thread(target = run_server)
t.start()

# make app show up as frontmost app
system_feedback = subprocess.Popen([
    "/usr/bin/osascript",
    "-e",
    "tell app \"Finder\" to set frontmost of process \"%s\" to true" % app_name],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    close_fds=True).communicate()[0].rstrip().decode("utf-8")

# Create a resizable webview window with 800x600 dimensions
webview.create_window("PyBrowse", "http://" + ip + ":" + port + "/pages/", width=1024,
                       height=768, resizable=True, fullscreen=False, debug=True)
