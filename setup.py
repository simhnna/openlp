#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=80 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2010 Raoul Snyman                                        #
# Portions copyright (c) 2008-2010 Tim Bentley, Jonathan Corwin, Michael      #
# Gorven, Scott Guerrieri, Christian Richter, Maikel Stuivenberg, Martin      #
# Thompson, Jon Tibble, Carsten Tinggaard                                     #
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

from setuptools import setup, find_packages

VERSION_FILE = 'openlp/.version'

try:
    from bzrlib.branch import Branch
    b = Branch.open_containing('.')[0]
    b.lock_read()
    try:
        # Get the branch's latest revision number.
        revno = b.revno()
        # Convert said revision number into a bzr revision id.
        revision_id = b.dotted_revno_to_revision_id((revno,))
        # Get a dict of tags, with the revision id as the key.
        tags = b.tags.get_reverse_tag_dict()
        # Check if the latest
        if revision_id in tags:
            version = u'%s' % tags[revision_id][0]
        else:
            version = '%s-bzr%s' % (sorted(b.tags.get_tag_dict().keys())[-1], revno)
        ver_file = open(VERSION_FILE, u'w')
        ver_file.write(version)
        ver_file.close()
    finally:
        b.unlock()
except:
    ver_file = open(VERSION_FILE, u'r')
    version = ver_file.read().strip()
    ver_file.close()


setup(
    name='OpenLP',
    version=version,
    description="Open source Church presentation and lyrics projection application.",
    long_description="""\
OpenLP (previously openlp.org) is free church presentation software, or lyrics projection software, used to display slides of songs, Bible verses, videos, images, and even presentations (if PowerPoint is installed) for church worship using a computer and a data projector.""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='open source church presentation lyrics projection song bible display project',
    author='Raoul Snyman',
    author_email='raoulsnyman@openlp.org',
    url='http://openlp.org/',
    license='GNU General Public License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    scripts=['openlp.pyw', 'scripts/openlp-1to2-converter.py', 'scripts/bible-1to2-converter.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """
)
