#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2016 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################

import json
import urllib
import urllib.request
import datetime
import sys
from subprocess import Popen, PIPE

token = 'xx'
webhook_url = 'https://ci.appveyor.com/api/subversion/webhook?id=x'
branch = 'lp:openlp'

webhook_element = \
{
    "commit": {
        "author": {
            "email": "open@contributer",
            "name": "OpenLP Contributor"
        },
        "id": None,
        "message": "Building " + branch,
        "timestamp": datetime.datetime.now().isoformat()
    },
    "config": None,
    "repository": {
        "name": "repo_name",
        "url": "repo_url"
    }
}


def get_version():
    """
    Get the version of the branch.
    """
    bzr = Popen(('bzr', 'tags'), stdout=PIPE)
    output = bzr.communicate()[0]
    code = bzr.wait()
    if code != 0:
        raise Exception('Error running bzr tags')
    lines = output.splitlines()
    if len(lines) == 0:
        tag = '0.0.0'
        revision = '0'
    else:
        tag, revision = lines[-1].decode('utf-8').split()
    bzr = Popen(('bzr', 'log', '--line', '-r', '-1'), stdout=PIPE)
    output, error = bzr.communicate()
    code = bzr.wait()
    if code != 0:
        raise Exception('Error running bzr log')
    latest = output.decode('utf-8').split(':')[0]
    version_string = latest == revision and tag or '%s-bzr%s' % (tag, latest)
    # Save decimal version in case we need to do a portable build.
    version = latest == revision and tag or '%s.%s' % (tag, latest)
    return version_string, version


def get_yml():
    f = open('appveyor.yml')
    yml_text = f.read()
    f.close()
    yml_text = yml_text.replace('BRANCHNAME', branch)
    return yml_text


def hook(token, webhook_url):
    webhook_element['config'] = get_yml()
    webhook_element['commit']['message'] = 'Building ' + branch
    version_string, version = get_version()
    webhook_element['commit']['id'] = version_string
    request = urllib.request.Request(webhook_url)
    print(json.dumps(webhook_element))
    request.add_header('Content-Type','application/json;charset=utf-8')
    request.add_header('Authorization', 'Bearer ' + token)
    responce = urllib.request.urlopen(request, json.dumps(webhook_element).encode('utf-8'))
    print(responce.read().decode('utf-8'))


hook(token, webhook_url)
