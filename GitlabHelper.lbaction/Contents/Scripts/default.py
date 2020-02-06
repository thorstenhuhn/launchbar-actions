#!/usr/local/bin/python

import json
import os
import subprocess
import sys
import tempfile

import action_impl

# default file locations
prefs_file = os.path.join(os.environ.get('LB_SUPPORT_PATH', tempfile.gettempdir()), 'Preferences.json')
cache_file = os.path.join(os.environ.get('LB_CACHE_PATH', tempfile.gettempdir()), 'Cache.json')

if len(sys.argv) > 1:
    action = sys.argv[1]
else:
    action = None

# init preferences
try:
    with open(prefs_file, 'r') as infile:
        prefs = json.load(infile)
except IOError as e:
    prefs = action_impl.get_default_preferences()
    with open(prefs_file, 'w') as outfile:
        json.dump(prefs, outfile)

# default action
if action is None:

    items = [ {
        'icon': 'font-awesome:fa-refresh',
        'title': 'Update cache',
        'action': 'default.py',
        'actionArgument': 'update',
        'actionReturnsItems': False,
        'actionRunsInBackground': False
    },
    {
        'icon': 'font-awesome:fa-gear',
        'title': 'Edit preferences',
        'subtitle': '',
        'path': prefs_file
    }
    ]

    try:
        with open(cache_file) as infile:
            data = json.load(infile)

        items.extend(data)

    except IOError:
        pass

else:

    try:
        items = getattr(action_impl, action)(prefs)
        if action == 'update':
            with open(cache_file, 'w') as outfile:
                json.dump(items, outfile)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        applescript='''
        tell application "LaunchBar"
            display alert "{}"
            hide
        end tell
        '''.format(str(e) + "(" + fname + ":" + str(exc_tb.tb_lineno) + ")")
        subprocess.Popen(['osascript', '-e', applescript], stdout=subprocess.PIPE)
        exit(0)

print(json.dumps(items, indent=4))

