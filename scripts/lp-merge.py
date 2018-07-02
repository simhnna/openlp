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
This script is used by developers to merge branches from launchpad.net into
other branches, which is basically what happens every time a merge proposal
is merged into trunk. This script simplifies the process and helps avoiding
merging to the wrong branch by doing some checks.
For the script to work it is assumed that the developer doing the merging
has a checkout (not branch) of the target branch.

Merge a branch
--------------
Once a branch has been approved for merging, go to the local folder with the
checkout of the target branch, copy the url from the merge proposal on launchpad
and use it like this:

    script/lp-merge.py <url>

The url could look like this:
https://code.launchpad.net/~tomasgroth/openlp/doc22update4/+merge/271874

First you'll be asked whether to merge the branch from the url to the local
branch, which will be done if you answer 'y'. The script checks that the current
folder is the right one before merging.
Then you'll be asked whether to commit the changes to the branch. The script
shows the command it will run, including detected linked bugs and author. If you
wish to change it, you can chose to run 'qcommit', an bzr GUI. Note that you'll
have to install qbzr for this to work. If you choose to run qcommit the script
will print the detected bugs + author for easy copying into the GUI.
"""
import subprocess
import re
import os
from urllib.request import urlopen
from urllib.error import HTTPError
from argparse import ArgumentParser
from bs4 import BeautifulSoup


def parse_args():
    """
    Parse command line arguments and return them
    """
    parser = ArgumentParser(prog='lp-merge', description='A helper script to merge proposals on Launchpad')
    parser.add_argument('url', help='URL to the merge proposal')
    parser.add_argument('-y', '--yes-to-all', action='store_true', help='Presume yes for all queries')
    parser.add_argument('-q', '--use-qcommit', action='store_true', help='Use qcommit for committing')
    return parser.parse_args()


def is_merge_url_valid(url):
    """
    Determine if the merge URL is valid
    """
    match = re.match(r'.+?/\+merge/\d+', url)
    if not url.startswith('https://code.launchpad.net/~') or match is None:
        print('The url is not valid! It should look like this:\n    '
              'https://code.launchpad.net/~myusername/openlp/mybranch/+merge/271874')
        return False
    return True


def get_merge_info(url):
    """
    Get all the merge information and return it as a dictionary
    """
    merge_info = {}
    print('Fetching merge information...')
    # Try to load the page
    try:
        page = urlopen(url)
    except HTTPError:
        print('Unable to load merge URL: {}'.format(url))
        return None
    soup = BeautifulSoup(page.read(), 'lxml')
    # Find the span tag that contains the branch url
    # <span class="branch-url">
    span_branch_url = soup.find('span', class_='branch-url')
    if not span_branch_url:
        print('Unable to find merge details on URL: {}'.format(url))
        return None
    merge_info['branch_url'] = span_branch_url.contents[0]
    # Find the p tag that contains the commit message
    # <div id="commit-message">...<div id="edit-commit_message">...<div class="yui3-editable_text-text"><p>
    commit_message = soup.find('div', id='commit-message').find('div', id='edit-commit_message') \
        .find('div', 'yui3-editable_text-text').p
    merge_info['commit_message'] = commit_message.string
    # Find all tr-tags with this class. Makes it possible to get bug numbers.
    # <tr class="bug-branch-summary"
    bug_rows = soup.find_all('tr', class_='bug-branch-summary')
    merge_info['bugs'] = []
    for row in bug_rows:
        id_attr = row.get('id')
        merge_info['bugs'].append(id_attr[8:])
    # Find target branch name using the tag below
    # <div class="context-publication"><h1>Merge ... into...
    div_branches = soup.find('div', class_='context-publication')
    branches = div_branches.h1.contents[0]
    merge_info['target_branch'] = '+branch/' + branches[(branches.find(' into lp:') + 9):]
    # Find the authors email address. It is hidden in a javascript line like this:
    # conf = {"status_value": "Needs review", "source_revid": "tomasgroth@yahoo.dk-20160921204550-gxduegmcmty9rljf",
    #         "user_can_edit_status": false, ...
    script_tag = soup.find('script', attrs={"id": "codereview-script"})
    content = script_tag.contents[0]
    start_pos = content.find('source_revid') + 16
    pattern = re.compile(r'.*\w-\d\d\d\d\d+')
    match = pattern.match(content[start_pos:])
    merge_info['author_email'] = match.group()[:-15]
    # Launchpad doesn't supply the author's true name, so we'll just grab whatever they use for display on LP
    a_person = soup.find('div', id='registration').find('a', 'person')
    merge_info['author_name'] = a_person.contents[0]
    return merge_info


def do_merge(merge_info, yes_to_all=False):
    """
    Do the merge
    """
    # Check that we are in the right branch
    bzr_info_output = subprocess.check_output(['bzr', 'info'])
    if merge_info['target_branch'] not in bzr_info_output.decode():
        print('ERROR: It seems you are not in the right folder...')
        return False
    # Merge the branch
    if yes_to_all:
        can_merge = True
    else:
        user_choice = input('Merge ' + merge_info['branch_url'] + ' into local branch? (y/N/q): ').lower()
        if user_choice == 'q':
            return False
        can_merge = user_choice == 'y'
    if can_merge:
        print('Merging...')
        subprocess.call(['bzr', 'merge', merge_info['branch_url']])
    return True


def qcommit(commit_message, author_name, author_email, bugs=[]):
    """
    Use qcommit to make the commit
    """
    # Setup QT workaround to make qbzr look right on my box
    my_env = os.environ.copy()
    my_env['QT_GRAPHICSSYSTEM'] = 'native'
    # Print stuff that kan be copy/pasted into qbzr GUI
    if bugs:
        print('These bugs can be copy/pasted in: ' + ' '.join(['lp:{}'.format(bug) for bug in bugs]))
    print('The authors email is: {} <{}>'.format(author_name, author_email))
    # Run qcommit
    subprocess.call(['bzr', 'qcommit', '-m', commit_message], env=my_env)


def do_commit(merge_info, yes_to_all=False, use_qcommit=False):
    """
    Actually do the commit
    """
    if use_qcommit:
        qcommit(merge_info['commit_message'], merge_info['author_name'], merge_info['author_email'],
                merge_info.get('bugs'))
        return True
    # Create commit command
    commit_command = ['bzr', 'commit']
    if 'bugs' in merge_info:
        commit_command.extend(['--fixes=lp:{}'.format(bug) for bug in merge_info['bugs']])
    commit_command.extend(['-m', merge_info['commit_message'],
                           '--author', '{author_name} <{author_email}>'.format(**merge_info)])
    if yes_to_all:
        can_commit = True
    else:
        print('About to run the bzr command below:\n')
        print(' '.join(commit_command))
        user_choice = input('Run the command (y), use qcommit (q) or cancel (C): ').lower()
        if user_choice == 'q':
            qcommit(merge_info['commit_message'], merge_info['author_name'], merge_info['author_email'],
                    merge_info.get('bugs'))
            return True
        can_commit = user_choice == 'y'
    if can_commit:
        print('Committing...')
        subprocess.call(commit_command)
        return True
    else:
        return False


def main():
    """
    Run the script
    """
    args = parse_args()
    if not is_merge_url_valid(args.url):
        exit(1)
    merge_info = get_merge_info(args.url)
    if not merge_info:
        exit(2)
    if not do_merge(merge_info, args.yes_to_all):
        exit(3)
    if not do_commit(merge_info, args.yes_to_all, args.use_qcommit):
        exit(4)


if __name__ == '__main__':
    main()
