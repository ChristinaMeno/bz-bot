#!/usr/bin/env python3

import subprocess
import requests
import sys
import os
from pprint import pprint
from string import Template

url = "https://bugzilla.redhat.com"
user = os.environ.get('BZ_NAME')
password = os.environ.get('BZ_PASS')
fields_we_like = "&include_fields=id,status,priority,severity,summary,target_release,creator,component"
product = "Red Hat Ceph Storage"
components = ["Build", "Ceph-Metrics", "Ceph-Volume", "Distribution"]
cee_group = []
qe_group = []

def get_login_token():
    r = requests.get(url + '/rest/login?login=' + user + '&password=' + password)
    token = r.json().get("token")
    return token

def get_bugs_that(token, data={"priority":"unspecified"}):
    bugs = {}
    data['token'] = token
    pri_params = Template("/rest/bug?token=$token&product=$product&component=$component&bug_status=__open__&$priority").substitute(data)
    r = requests.get(url + pri_params + fields_we_like)
    bug_tuple = [(x.get('id'), x) for x in r.json().get('bugs')]
    bugs.update(dict(bug_tuple))

    return bugs


def get_one_bug(id, token):
    data = {'token': token, 'id': id}
    params = Template("/rest/bug/$id?token=$token").substitute(data)
    r = requests.get(url + params)
    pprint(r.json())


def update_bugs(token, bugs):
    for k,v in bugs.items():
        pprint(k)
        pprint(v)
        pri = v.get('priority')
        sev = v.get('severity')
        if pri == "unspecified" and sev == "unspecified":
            choice = input("pri and sev is one of [low, medium, high, urgent] = ")
            if choice in ('low', 'medium', 'high', 'urgent'):
                pprint("update")
                r = requests.put(url + "/rest/bug/%d?token=%s" % (k, token), data = {"priority": choice,"severity": choice})

        elif pri == "unspecified":
            pprint (subprocess.run(["/usr/bin/open", "https://bugzilla.redhat.com/show_bug.cgi?id=%d" % k]))
            pprint ("would set priority to %s" % sev)
            choice = input("y / n")
            if choice == 'y':
                pprint("update")
                #r = requests.put(url + "/rest/bug/%d?token=%s" % (k, token), data = {"priority": sev})
            else:
                continue
        elif sev == "unspecified":
            pprint (subprocess.run(["/usr/bin/open", "https://bugzilla.redhat.com/show_bug.cgi?id=%d" % k]))
            pprint ("would set severity to %s" % pri)
            choice = input("y / n")
            if choice == 'y':
                pprint("update")
                #r = requests.put(url + "/rest/bug/%d?token=%s" % (k, token), data = {"severity": pri})
            else:
                continue
        else:
            pprint("WTF")


def main():
    bugs = {}
    token = get_login_token()
    print("got a token" + token)
    for component in components:
        b = get_bugs_that(token, {'product': product,
                            'component': component,
                            'priority': 'priority=unspecified'})
        bugs.update(b)
        b = get_bugs_that(token, {'product': product,
                            'component': component,
                            'priority': 'severity=unspecified'})
        bugs.update(b)

    update_bugs(token, bugs)

if __name__ == "__main__":
    main()
