import json
import urllib2

def gitlab_query(url, gitlab_token):

    request = urllib2.Request(url)
    request.add_header('PRIVATE-TOKEN', gitlab_token)

    response = urllib2.urlopen(request)
    result = json.loads(response.read())
    if response.info().getheader('X-Next-Page'):
        link_header = response.info().getheader('Link')
        for link_definition in link_header.split(', '):
            link, rel = link_definition.split('; rel=')
            if rel.strip('\"') == "next":
                result.extend(gitlab_query(link.strip('<').strip('>'), gitlab_token))
                break

    return result

def get_default_preferences():

    return {
        'gitlab_url': '<your-gitlab-url-here>',
        'gitlab_token': '<your-access-token-here>'
    }

def update(preferences):

    gitlab_url = preferences.get('gitlab_url')
    gitlab_token = preferences.get('gitlab_token')

    # get all groups the current user is a member of
    data = gitlab_query(gitlab_url + '/api/v4/groups?per_page=50&membership=true', gitlab_token)

    group_map = {}
    for group in data:
        gid = group['id']
        if not gid in group_map:
            group_map[gid] = {}
            group_map[gid]['title'] = group['name']
            group_map[gid]['subtitle'] = group['description'] or ''
            group_map[gid]['icon'] = 'font-awesome:fa-folder-o'
            group_map[gid]['children'] = [{ 'title': 'Group Home', 'url': group['web_url'], 'icon': 'font-awesome:home' }]

        if not 'title' in group_map[gid]:
            group_map[gid]['title'] = group['name']
            group_map[gid]['subtitle'] = group['description'] or ''
            group_map[gid]['icon'] = 'font-awesome:fa-folder-o'
            group_map[gid]['children'].append({ 'title': 'Group Home', 'url': group['web_url'], 'icon': 'font-awesome:home' })

        pid = group['parent_id'] or 'root'
        if not pid in group_map:
            group_map[pid] = {}
            group_map[pid]['children'] = []

        group_map[pid]['children'].append(group_map[gid])

    # get all projects the current user is a member of
    data = gitlab_query(gitlab_url + '/api/v4/projects?per_page=50&membership=true', gitlab_token)

    for project in data:
        p = {}
        p['title'] = project['name']
        p['subtitle'] = project['description'] or ''
        p['badge'] = project['namespace']['full_path']
        p['icon'] = 'font-awesome:fa-bookmark-o'
        p['children'] = [
            { 'title': 'Project home', 'url': project['web_url'], 'icon': 'font-awesome:home' },
            { 'title': 'Copy Clone URL', 'action': 'clipboard.sh', 'actionArgument': project['ssh_url_to_repo'], 'actionRunsInBackground': True, 'icon': 'font-awesome:clipboard' },
            { 'title': 'Pipelines', 'url': project['web_url'] + '/pipelines', 'icon': 'font-awesome:rocket' }
        ]

        nid = project['namespace']['id']
        if nid in group_map:
            group_map[nid]['children'].append(p)
        group_map['root']['children'].append(p)

    return group_map['root']['children']

