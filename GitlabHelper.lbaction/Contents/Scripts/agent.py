#!/usr/local/bin/python

import json
import os
import urllib2
import tempfile
import time
import sys

# =========================================================================== 
# functions

def gitlab_query(url):
    request = urllib2.Request(url)
    request.add_header('PRIVATE-TOKEN', gitlab_token)
    try:
        response = urllib2.urlopen(request)
        result = json.loads(response.read())
        if response.info().getheader('X-Next-Page'):
            link_header = response.info().getheader('Link')
            for link_definition in link_header.split(', '):
                link, rel = link_definition.split('; rel=')
                if rel.strip('\"') == "next":
                    result.extend(gitlab_query(link.strip('<').strip('>')))
                    break
    except Exception as e:
        print(e)
        exit(0)
    return result

# =========================================================================== 
# main

preffile = os.path.join(os.environ.get('LB_SUPPORT_PATH', tempfile.gettempdir()), 'preferences.json')
try:
    with open(preffile) as infile:
        preferences = json.load(infile)
except IOError:
    preferences = {}

if 'gitlab_url' not in preferences or 'gitlab_token' not in preferences:
    print("Preferences not set! Aborting.")
    exit(1)

gitlab_url = preferences['gitlab_url']
gitlab_token = preferences['gitlab_token']

statefile = os.path.join(os.environ.get('LB_CACHE_PATH', tempfile.gettempdir()), 'projects.json')

# get all groups the current user is a member of
data = gitlab_query(gitlab_url + '/api/v4/groups?per_page=50&membership=true')

group_map = {}
for group in data:
    gid = group['id']
    if not gid in group_map:
        group_map[gid] = {}
        group_map[gid]['title'] = group['name']
        group_map[gid]['subtitle'] = group['description'] or ''
        group_map[gid]['icon'] = 'font-awesome:folder'
        group_map[gid]['children'] = [{ 'title': 'Group Home', 'url': group['web_url'], 'icon': 'font-awesome:home' }]

    if not 'title' in group_map[gid]:
        group_map[gid]['title'] = group['name']
        group_map[gid]['subtitle'] = group['description'] or ''
        group_map[gid]['icon'] = 'font-awesome:folder'
        group_map[gid]['children'].append({ 'title': 'Group Home', 'url': group['web_url'], 'icon': 'font-awesome:home' })

    pid = group['parent_id'] or 'root'
    if not pid in group_map:
        group_map[pid] = {}
        group_map[pid]['children'] = []

    group_map[pid]['children'].append(group_map[gid])

# get all projects the current user is a member of
data = gitlab_query(gitlab_url + '/api/v4/projects?per_page=50&membership=true')

for project in data:
    p = {}
    p['title'] = project['name']
    p['subtitle'] = project['description'] or ''
    p['badge'] = project['namespace']['full_path']
    p['icon'] = 'font-awesome:bookmark'
    p['children'] = [
        { 'title': 'Project home', 'url': project['web_url'], 'icon': 'font-awesome:home' },
        { 'title': 'Copy Clone URL', 'action': 'clipboard.sh', 'actionArgument': project['ssh_url_to_repo'], 'actionRunsInBackground': True, 'icon': 'font-awesome:clipboard' },
        { 'title': 'Pipelines', 'url': project['web_url'] + '/pipelines', 'icon': 'font-awesome:rocket' }
    ]

    nid = project['namespace']['id']
    if nid in group_map:
        group_map[nid]['children'].append(p)
    group_map['root']['children'].append(p)

# write to cache
with open(statefile, 'w') as outfile:
    json.dump(group_map['root']['children'], outfile)

