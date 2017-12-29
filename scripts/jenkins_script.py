#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2018 OpenLP Developers                                   #
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
This script helps to trigger builds of branches. To use it you have to install the python-jenkins module. On Fedora
and Ubuntu/Debian, it is available as the ``python3-jenkins`` package::

    $ sudo dnf/apt install python3-jenkins

To make it easier to run you may want to create a shell script or an alias. To create an alias, add this to your
``~/.bashrc`` (or ``~/.zshrc``) file and then log out and log back in again (to apply the alias)::

    alias ci="python3 /path/to/openlp_root/scripts/jenkins_script.py -u USERNAME -p PASSWORD"

To create a shell script, create the following file in a location in your ``$PATH`` (I called mine ``ci``)::

    #!/bin/bash
    python3 /path/to/openlp_root/scripts/jenkins_script.py -u USERNAME -p PASSWORD

``USERNAME`` is your Jenkins username, and ``PASSWORD`` is your Jenkins password or personal token.

An older version of this script used to use a shared TOKEN, but this has been replaced with the username and password.
"""
import os
import re
import time
from argparse import ArgumentParser
from subprocess import Popen, PIPE

from jenkins import Jenkins

JENKINS_URL = 'https://ci.openlp.io/'
REPO_REGEX = r'(.*/+)(~.*)'


class OpenLPJobs(object):
    """
    This class holds any jobs we have on jenkins and we actually need in this script.
    """
    Branch_Pull = 'Branch-01-Pull'
    Branch_Linux_Tests = 'Branch-02a-Linux-Tests'
    Branch_macOS_Tests = 'Branch-02b-macOS-Tests'
    Branch_Build_Source = 'Branch-03a-Build-Source'
    Branch_Build_macOS = 'Branch-03b-Build-macOS'
    Branch_Code_Analysis = 'Branch-04a-Code-Analysis'
    Branch_Test_Coverage = 'Branch-04b-Test-Coverage'
    Branch_Lint_Check = 'Branch-04c-Lint-Check'
    Branch_AppVeyor_Tests = 'Branch-05-AppVeyor-Tests'

    Jobs = [Branch_Pull, Branch_Linux_Tests, Branch_macOS_Tests, Branch_Build_Source, Branch_Build_macOS,
            Branch_Code_Analysis, Branch_Test_Coverage, Branch_AppVeyor_Tests]


class Colour(object):
    """
    This class holds values which can be used to print coloured text.
    """
    RED_START = '\033[1;31m'
    RED_END = '\033[1;m'
    GREEN_START = '\033[1;32m'
    GREEN_END = '\033[1;m'


class JenkinsTrigger(object):
    """
    A class to trigger builds on Jenkins and print the results.

    :param token: The token we need to trigger the build. If you do not have this token, ask in IRC.
    """

    def __init__(self, username, password, can_use_colour):
        """
        Create the JenkinsTrigger instance.
        """
        self.jobs = {}
        self.can_use_colour = can_use_colour and not os.name.startswith('nt')
        self.repo_name = get_repo_name()
        self.server = Jenkins(JENKINS_URL, username=username, password=password)

    def fetch_jobs(self):
        """
        Get the job info for all the jobs
        """
        for job_name in OpenLPJobs.Jobs:
            job_info = self.server.get_job_info(job_name)
            self.jobs[job_name] = job_info
            self.jobs[job_name]['nextBuildUrl'] = '{url}{nextBuildNumber}/'.format(**job_info)

    def trigger_build(self):
        """
        Ask our jenkins server to build the "Branch-01-Pull" job.
        """
        bzr = Popen(('bzr', 'whoami'), stdout=PIPE, stderr=PIPE)
        raw_output, error = bzr.communicate()
        # We just want the name (not the email).
        name = ' '.join(raw_output.decode().split()[:-1])
        cause = 'Build triggered by %s (%s)' % (name, self.repo_name)
        self.fetch_jobs()
        self.server.build_job(OpenLPJobs.Branch_Pull, {'BRANCH_NAME': self.repo_name, 'cause': cause})

    def print_output(self, can_continue=False):
        """
        Print the status information of the build triggered.
        """
        print('Add this to your merge proposal:')
        print('-' * 80)
        bzr = Popen(('bzr', 'revno'), stdout=PIPE, stderr=PIPE)
        raw_output, error = bzr.communicate()
        revno = raw_output.decode().strip()
        print('%s (revision %s)' % (get_repo_name(), revno))

        failed_builds = []
        for job in OpenLPJobs.Jobs:
            if not self.__print_build_info(job):
                if self.current_build:
                    failed_builds.append((self.current_build['fullDisplayName'], self.current_build['url']))
                if not can_continue:
                    print('Stopping after failure')
                    break
        print('')
        if failed_builds:
            print('Failed builds:')
            for build_name, url in failed_builds:
                print(' - {}: {}console'.format(build_name, url))
        else:
            print('All builds passed')

    def open_browser(self):
        """
        Opens the browser.
        """
        url = self.jenkins_instance.job(OpenLPJobs.Branch_Pull).info['url']
        # Open the url
        Popen(('xdg-open', url), stderr=PIPE)

    def _get_build_info(self, job_name, build_number):
        """
        Get the build info from the server. This method will check the queue and wait for the build.
        """
        queue_info = self.server.get_queue_info()
        tries = 0
        while queue_info and tries < 50:
            tries += 1
            time.sleep(0.75)
            queue_info = self.server.get_queue_info()
        if tries >= 50:
            raise Exception('Build has not started yet, it may be stuck in the queue.')
        return self.server.get_build_info(job_name, build_number)

    def __print_build_info(self, job_name):
        """
        This helper method prints the job information of the given ``job_name``

        :param job_name: The name of the job we want the information from. For example *Branch-01-Pull*. Use the class
         variables from the :class:`OpenLPJobs` class.
        """
        job = self.jobs[job_name]
        print('{:<70} [WAITING]'.format(job['nextBuildUrl']), end='', flush=True)
        self.current_build = self._get_build_info(job_name, job['nextBuildNumber'])
        print('\b\b\b\b\b\b\b\b\b[RUNNING]', end='', flush=True)
        is_success = False
        while self.current_build['building'] is True:
            time.sleep(0.5)
            self.current_build = self.server.get_build_info(job_name, job['nextBuildNumber'])
        result_string = self.current_build['result']
        is_success = result_string == 'SUCCESS'
        if self.can_use_colour:
            if is_success:
                # Make 'SUCCESS' green.
                result_string = '{}{}{}'.format(Colour.GREEN_START, result_string, Colour.GREEN_END)
            else:
                # Make 'FAILURE' red.
                result_string = '{}{}{}'.format(Colour.RED_START, result_string, Colour.RED_END)
        print('\b\b\b\b\b\b\b\b\b[{:>7}]'.format(result_string))
        return is_success


def get_repo_name():
    """
    This returns the name of branch of the working directory. For example it returns *lp:~googol/openlp/render*.
    """
    # Run the bzr command.
    bzr = Popen(('bzr', 'info'), stdout=PIPE, stderr=PIPE)
    raw_output, error = bzr.communicate()
    # Detect any errors
    if error:
        print('This is not a branch.')
        return
    # Clean the output.
    raw_output = raw_output.decode()
    output_list = list(map(str.strip, raw_output.split('\n')))
    # Determine the branch's name
    repo_name = ''
    for line in output_list:
        # Check if it is api branch.
        if 'push branch' in line:
            match = re.match(REPO_REGEX, line)
            if match:
                repo_name = 'lp:%s' % match.group(2)
                break
        elif 'checkout of branch' in line:
            match = re.match(REPO_REGEX, line)
            if match:
                repo_name = 'lp:%s' % match.group(2)
                break
    return repo_name.strip('/')


def main():
    """
    Run the script
    """
    parser = ArgumentParser()
    parser.add_argument('-d', '--disable-output', action='store_true', default=False, help='Disable output')
    parser.add_argument('-b', '--open-browser', action='store_true', default=False,
                        help='Opens the jenkins page in your browser')
    parser.add_argument('-n', '--no-colour', action='store_true', default=False,
                        help='Disable coloured output (always disabled on Windows)')
    parser.add_argument('-u', '--username', required=True, help='Your Jenkins username')
    parser.add_argument('-p', '--password', required=True, help='Your Jenkins password or personal token')
    parser.add_argument('-c', '--always-continue', action='store_true', default=False, help='Continue despite failure')
    args = parser.parse_args()

    if not get_repo_name():
        print('Not a branch. Have you pushed it to launchpad? Did you cd to the branch?')
        return
    jenkins_trigger = JenkinsTrigger(args.username, args.password, not args.no_colour)
    jenkins_trigger.trigger_build()
    # Open the browser before printing the output.
    if args.open_browser:
        jenkins_trigger.open_browser()
    if not args.disable_output:
        jenkins_trigger.print_output(can_continue=args.always_continue)


if __name__ == '__main__':
    main()
