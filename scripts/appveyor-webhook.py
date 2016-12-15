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

"""
This script is used to trigger a build at appveyor. Since the code is not hosted
on github the normal triggering mechanisms can't be use. The project is
registered as subversion repository. A webhook is used to trigger new builds.
The appveyor.yml used for the build is send to appveyor when calling the hook.
"""
import json
import urllib
import urllib.request
import datetime
import sys
import time
from subprocess import Popen, PIPE

appveyor_build_url = 'https://ci.appveyor.com/project/TomasGroth/openlp/build'
appveyor_api_url = 'https://ci.appveyor.com/api/projects/TomasGroth/openlp'

webhook_element = \
    {
        'commit': {
            'author': {
                'email': 'open@contributer',
                'name': 'OpenLP Contributor'
            },
            'id': None,
            'message': None,
            'timestamp': datetime.datetime.now().isoformat()
        },
        'config': None,
        'repository': {
            'name': 'repo_name',
            'url': 'repo_url'
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
    version_string = latest == revision and tag or 'r%s' % latest
    # Save decimal version in case we need to do a portable build.
    version = latest == revision and tag or '%s.%s' % (tag, latest)
    return version_string, version


def get_yml(branch):
    """
    Returns the content of appveyor.yml and inserts the branch to be build
    """
    f = open('appveyor.yml')
    yml_text = f.read()
    f.close()
    yml_text = yml_text.replace('BRANCHNAME', branch)
    return yml_text


def hook(webhook_url, yml):
    """
    Activate the webhook to start the build
    """
    webhook_element['config'] = yml
    webhook_element['commit']['message'] = 'Building ' + branch
    version_string, version = get_version()
    webhook_element['commit']['id'] = version_string
    request = urllib.request.Request(webhook_url)
    request.add_header('Content-Type', 'application/json;charset=utf-8')
    responce = urllib.request.urlopen(request, json.dumps(webhook_element).encode('utf-8'))
    if responce.getcode() != 204:
        print('An error happened when calling the webhook! Return code: %d' % responce.getcode())
        print(responce.read().decode('utf-8'))


def get_appveyor_build_url(branch):
    """
    Get the url of the build.
    """
    # Wait 10 seconds to make sure the hook has been triggered
    time.sleep(10)
    responce = urllib.request.urlopen(appveyor_api_url)
    json_str = responce.read().decode('utf-8')
    build_json = json.loads(json_str)
    build_url = '%s/%s' % (appveyor_build_url, build_json['build']['version'])
    print('Check this URL for build status: %s' % build_url)


if len(sys.argv) != 3:
    print('Usage: %s <webhook-url> <branch>' % sys.argv[0])
else:
    webhook_url = sys.argv[1]
    branch = sys.argv[2]
    hook(webhook_url, get_yml(branch))
    get_appveyor_build_url(branch)
