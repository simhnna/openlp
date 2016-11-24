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
This module contains tests for the WordProject Bible importer.
"""

import os
import json
from unittest import TestCase

from openlp.plugins.bibles.lib.importers.wordproject import WordProjectBible
from openlp.plugins.bibles.lib.db import BibleDB

from tests.functional import MagicMock, patch, call

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         '..', '..', '..', 'resources', 'bibles'))
INDEX_PAGE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>The Holy Bible in the English language with audio narration - KJV</title>
    <meta name="title" content="The Holy Bible in the English language with audio narration - KJV" />
<meta name="description" content="Bible books: choose the book you wish to read or listen to" />
<meta name="keywords" content="Bible, Holy, New testament, Old testament, Scriptures, God, Jesus" />
<link rel="shortcut icon" href="http://www.wordproject.org/favicon.ico" />
<meta name="robots" content="index, follow" />
	<!-- Mobile viewport optimisation -->
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<link rel="stylesheet" type="text/css" href="_assets/css/css.css" />
<link rel="stylesheet" type="text/css" href="_assets/css/style.css" />
<link rel="stylesheet" type="text/css" href="_assets/css/page-player.css" />
<link rel="stylesheet" type="text/css" href="_assets/css/tables_bibles.css" />

  <!--[if lte IE 7]>
	<link href="_assets/css/iehacks.css" rel="stylesheet" type="text/css" />
	<![endif]-->

	<!--[if lt IE 9]>
	<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->
    <!-- google analytics -->
    <script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-39700598-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>


    <style type="text/css">
<!--
.style1 {font-size: medium}
-->
    </style>
</head>
<a name="mytop"></a>
<body>
<header class="ym-noprint">
	<div class="ym-wrapper">
		<div class="ym-wbox">
			<h1><strong>Word</strong><em>Project</em></h1>
		</div>
	</div>
</header>
<!--index nav-->
<!--nav id="nav">
	<div class="ym-wrapper">
		<div class="ym-hlist">
			<ul>
				<li><a title="Home" href="../../index.htm" target="_top">Home</a></li>
          <li class="active"><a title="Bibles" href="../../bibles/index.htm" target="_self">Bibles</a></li>
				<li><a title="Audio Bible" href="../../bibles/audio/index.htm" target="_top">Audio</a></li>
				<li><a title="Selected Bible Verses" href="../../bibles/verses/index.htm" target="_top">Verses</a></li>
                <li><a title="Parallel Bibles" href="../../bibles/parallel/index.htm" target="_top">Multi</a></li>
				<li><a title="Resourcces" href="../../bibles/resources/index.htm" target="_top">Resources</a></li>
                <li><a title="Search" href="../../bibles/search/index.htm" target="_top">Search</a></li>
				<li><a title="Download this Bible [language]" href="../../download/bibles/index.htm" target="_top">Download</a></li>
			</ul>
		</div>
	</div>
</nav-->
<div class="ym-wrapper ym-noprint">
    	<div class="ym-wbox">
<!--share buttons-->
<div style="margin: 10px 1px 5px 20px;" align="right">
<!-- Facebook -->
<a title="Click to share on Facebook" href="http://www.facebook.com/sharer.php?u=http://wordproject.org/bibles/kj/index.htm" target="_blank"><img src="_assets/img/facebook_2.png" alt="facebook" /></a>
<!-- Twitter -->
<a title="Click to share on Twitter" href="http://twitter.com/share?url=http://wordproject.org/bibles/kj/index.htm&text=Read this page &hashtags=wordproject" target="_blank"><img src="_assets/img/twitter_2.png" alt="twitter" /></a>
<!-- Google+ -->
<a title="Click to share on Google plus" href="https://plus.google.com/share?url=http://wordproject.org/bibles/kj/index.htm" target="_blank"><img src="_assets/img/google+_2.png" alt="google" /></a>
<!-- LinkedIn -->
<a title="Click to share on Linkedin" href="http://www.linkedin.com/shareArticle?mini=true&url=http://www.wordproject.org" target="_blank"><img src="_assets/img/linkin_2.png" alt="linkin" /></a></p>
</div>
<!--/share buttons-->
        <div class=" ym-grid">
        <div class="ym-g62 ym-gl breadCrumbs"> <a title="Home" href="http://www.wordproject.org/index.htm" target="_top">Home</a> / <!--a title="Bibles" href="../index.htm" target="_self">Bibles</a--> /  </div>
	<div class="ym-g38 ym-gr alignRight ym-noprint"><a class="decreaseFont ym-button">-</a><a class="resetFont ym-button">Reset</a><a class="increaseFont ym-button">+</a>
	</div>
</div>
</div>
</div>
<div id="main" class="ym-clearfix" role="main">
	<div class="ym-wrapper">
    	<div class="ym-wbox">
        <div class="textOptions">
<div class="textHeader">
  <h2>English Bible </h2><span class="faded">King James Version</span>
<a name="0"></a>
  <p class="faded">Please, choose a book  of the Holy Bible in the English language:</p>
<hr />
</div>
<div class="ym-grid linearize-level-2">
   <!-- chapter list -->
  <div class="ym-g50 ym-gl">
  <h3>Old Testament</h3>
    <ul id="maintab" class="shadetabs">
    <li><a href="01/1.htm">[1] Genesis <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="02/1.htm">[2] Exodus <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="03/1.htm">[3] Leviticus <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="04/1.htm">[4] Numbers <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="05/1.htm">[5] Deuteronomy <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="06/1.htm">[6] Joshua <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="07/1.htm">[7] Judges <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="08/1.htm">[8] Ruth <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="09/1.htm">[9] 1 Samuel <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="10/1.htm">[10] 2 Samuel <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="11/1.htm">[11] 1 Kings <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="12/1.htm">[12] 2 Kings <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="13/1.htm">[13] 1 Chronicles <i class="icon-headphones pull-right"></i> </a></li>
    <li><a href="14/1.htm">[14] 2 Chronicles <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="15/1.htm">[15] Ezra <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="16/1.htm">[16] Nehemiah <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="17/1.htm">[17] Esther <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="18/1.htm">[18] Job <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="19/1.htm">[19] Psalms <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="20/1.htm">[20] Proverbs <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="21/1.htm">[21] Ecclesiastes <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="22/1.htm">[22] Song of Songs <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="23/1.htm">[23] Isaiah <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="24/1.htm">[24] Jeremiah <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="25/1.htm">[25] Lamentations <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="26/1.htm">[26] Ezekiel <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="27/1.htm">[27] Daniel <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="28/1.htm">[28] Hosea <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="29/1.htm">[29] Joel <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="30/1.htm">[30] Amos <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="31/1.htm">[31] Obadiah <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="32/1.htm">[32] Jonah <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="33/1.htm">[33] Micah <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="34/1.htm">[34] Nahum <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="35/1.htm">[35] Habakkuk <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="36/1.htm">[36] Zephaniah <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="37/1.htm">[37] Haggai <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="38/1.htm">[38] Zechariah <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="39/1.htm">[39] Malachi <i class="icon-headphones pull-right"></i></a></li>
  </ul>
  </div> <div class="ym-g50 ym-gr">
  <h3>New Testament</h3>
  	<ul id="maintab" class="shadetabs">
    <li><a href="40/1.htm">[40] Matthew <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="41/1.htm">[41] Mark <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="42/1.htm">[42] Luke <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="43/1.htm">[43] John <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="44/1.htm">[44] Acts <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="45/1.htm">[45] Romans <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="46/1.htm">[46] 1 Corinthians <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="47/1.htm">[47] 2 Corinthians <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="48/1.htm">[48] Galatians <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="49/1.htm">[49] Ephesians <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="50/1.htm">[50] Philippians <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="51/1.htm">[51] Colossians <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="52/1.htm">[52] 1 Thessalonians <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="53/1.htm">[53] 2 Thessalonians <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="54/1.htm">[54] 1 Timothy <i class="icon-headphones pull-right"></i></a></li>
    <li> <a href="55/1.htm">[55] 2 Timothy <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="56/1.htm">[56] Titus <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="57/1.htm">[57] Philemon <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="58/1.htm">[58] Hebrews <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="59/1.htm">[59] James <i class="icon-headphones pull-right"></i></a></li>
    <li> <a href="60/1.htm">[60] 1 Peter <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="61/1.htm">[61] 2 Peter <i class="icon-headphones pull-right"></i></a></li>
    <li> <a href="62/1.htm">[62] 1 John <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="63/1.htm">[63] 2 John <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="64/1.htm">[64] 3 John <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="65/1.htm">[65] Jude <i class="icon-headphones pull-right"></i></a></li>
    <li><a href="66/1.htm">[66] Revelation <i class="icon-headphones pull-right"></i></a></li>
    </ul>
    </div>
	 <!-- end chapter list -->
</div>

</div>
</div><!-- ym-wbox end -->
</div><!-- ym-wrapper end -->
</div><!-- ym-wrapper end -->
<div class="ym-wrapper">
    	<div class="ym-wbox">
<div class="alignRight ym-noprint">
  <p><a class="ym-button" href="#mytop"><i class="icon-circle-arrow-up icon-white"></i> Top</a>

</p>

</div>
</div>
</div>
<footer>
	<div class="ym-wrapper">
		<div class="ym-wbox">
			<p class="alignCenter">Wordproject® is a registered name of the <a href="http://www.wordproject.org">International Biblical Association</a>, a non-profit organization registered in Macau, China.	</p>
			<p class="alignCenter"><a href="http://www.wordproject.org/contact/new/index.htm" target="_top">Contact</a> | <a href="http://www.wordproject.org/contact/new/disclaim.htm" target="_top"> Disclaimer</a> |
			<a href="http://www.wordproject.org/contact/new/state.htm" target="_top">Statement of Faith</a> |
			<a href="http://www.wordproject.org/contact/new/mstate.htm" target="_top">Mission</a> |
			<a href="http://www.wordproject.org/contact/new/copyrights.htm" target="_top">Copyrights</a></p>
		</div>
	</div>
</footer>
</body>
</script><script type="text/javascript" src="_assets/js/jquery-1.8.0.min.js"></script>
<script type="text/javascript" src="_assets/js/soundmanager2.js"></script>
<script type="text/javascript" src="_assets/js/page-player.js"></script>
<script type="text/javascript" src="_assets/js/script.js"></script>
<script type="text/javascript">

soundManager.setup({
  url: '_assets/swf/'
});

</script>
</html>
"""
CHAPTER_PAGE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>Creation of the world, Genesis Chapter 1</title>
	<meta name="description" content="Creation of the world, Genesis Chapter 1" />
	<meta name="keywords" content="Holy Bible, Old Testament, scriptures,  Creation, faith, heaven, hell, God, Jesus" />
	<!-- Mobile viewport optimisation -->
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<link rel="stylesheet" type="text/css" href="../_assets/css/css.css" />
<link rel="stylesheet" type="text/css" href="../_assets/css/style.css" />
<link rel="stylesheet" type="text/css" href="../_assets/css/page-player.css" />
	
  <!--[if lte IE 7]>
	<link href="../_assets/css/iehacks.css" rel="stylesheet" type="text/css" />
	<![endif]-->
    <!-- google analytics -->
    <script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-39700598-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>

	<!--[if lt IE 9]>
	<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->
    <!-- google analytics -->
    <script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-39700598-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>

    
</head>
<a name="mytop"></a>
<body>
<header class="ym-noprint">
	<div class="ym-wrapper">
		<div class="ym-wbox">
			<h1><strong>Word</strong><em>Project</em></h1>
		</div>
	</div>
</header>
<!--lang nav-->
<!--nav id="nav">
	<div class="ym-wrapper">
		<div class="ym-hlist">
			<ul>
				<li><a title="Home" href="../../../index.htm" target="_top">Home</a></li>
         		<li class="active"><a title="Bibles" href="../../../bibles/index.htm" target="_self">Bibles</a></li>
				<li><a title="Audio Bible" href="../../../bibles/audio/01_english/b01.htm" target="_top">Audio</a></li>
				<li><a title="Selected Bible Verses" href="../../../bibles/verses/english/index.htm" target="_top">Verses</a></li>
                <li><a title="Parallel Bibles" href="../../../bibles/parallel/index.htm" target="_top">Multi</a></li>
				<li><a title="Resourcces" href="../../../bibles/resources/index.htm" target="_top">Resources</a></li>
                <li><a title="Search" href="../../../bibles/search/index.htm" target="_top">Search</a></li>
				<li><a title="Download this Bible [language]" href="../../../download/bibles/index.htm" target="_top">Download</a></li>
			</ul>
		</div>
	</div>
</nav-->
<div class="ym-wrapper ym-noprint">
    	<div class="ym-wbox">
<!--share buttons-->
<div style="margin: 10px 1px 5px 20px;" align="right">
<!-- Facebook -->
<a title="Click to share on Facebook" href="http://www.facebook.com/sharer.php?u=http://wordproject.org/bibles/kj/01/1.htm" target="_blank"><img src="../_assets/img/facebook_2.png" alt="facebook" /></a>
<!-- Twitter -->
<a title="Click to share on Twitter" href="http://twitter.com/share?url=http://wordproject.org/bibles/kj/01/1.htm&text=Read this page &hashtags=wordproject" target="_blank"><img src="../_assets/img/twitter_2.png" alt="twitter" /></a>
<!-- Google+ -->
<a title="Click to share on Google plus" href="https://plus.google.com/share?url=http://wordproject.org/bibles/kj/01/1.htm" target="_blank"><img src="../_assets/img/google+_2.png" alt="google" /></a>
<!-- LinkedIn -->
<a title="Click to share on Linkedin" href="http://www.linkedin.com/shareArticle?mini=true&url=http://www.wordproject.org" target="_blank"><img src="../_assets/img/linkin_2.png" alt="linkin" /></a></p>
</div>
<!--/share buttons-->
        <div class=" ym-grid">
        <div class="ym-g62 ym-gl breadCrumbs"> <!--a title="Home" href="http://www.wordproject.org/index.htm" target="_top">Home</a> / <a title="Bibles" href="../../index.htm" target="_self">Bibles</a--> /  <a href="../index.htm" target="_self">KJV</a></div>
<div class="ym-g38 ym-gr alignRight ym-noprint"><a class="decreaseFont ym-button">-</a><a class="resetFont ym-button">Reset</a><a class="increaseFont ym-button">+</a>
	</div>
</div>
</div>
</div>
<div id="main" class="ym-clearfix" role="main">
	<div class="ym-wrapper">
    	<div class="ym-wbox">
        <div class="textOptions">
<div class="textHeader">
  <h2>Genesis</h2>
<a name="0"></a>
<p class="ym-noprint"> Chapter: 
 
<span class="c1">1</span>
<a href="2.htm#0">2</a> 
<a href="3.htm#0">3</a> 
<a href="4.htm#0">4</a> 
<a href="5.htm#0">5</a> 
<a href="6.htm#0">6</a> 
<a href="7.htm#0">7</a> 
<a href="8.htm#0">8</a> 
<a href="9.htm#0">9</a> 
<a href="10.htm#0">10</a> 
<a href="11.htm#0">11</a> 
<a href="12.htm#0">12</a> 
<a href="13.htm#0">13</a> 
<a href="14.htm#0">14</a> 
<a href="15.htm#0">15</a> 
<a href="16.htm#0">16</a> 
<a href="17.htm#0">17</a> 
<a href="18.htm#0">18</a> 
<a href="19.htm#0">19</a> 
<a href="20.htm#0">20</a> 
<a href="21.htm#0">21</a> 
<a href="22.htm#0">22</a> 
<a href="23.htm#0">23</a> 
<a href="24.htm#0">24</a> 
<a href="25.htm#0">25</a> 
<a href="26.htm#0">26</a> 
<a href="27.htm#0">27</a> 
<a href="28.htm#0">28</a> 
<a href="29.htm#0">29</a> 
<a href="30.htm#0">30</a> 
<a href="31.htm#0">31</a> 
<a href="32.htm#0">32</a> 
<a href="33.htm#0">33</a> 
<a href="34.htm#0">34</a> 
<a href="35.htm#0">35</a> 
<a href="36.htm#0">36</a> 
<a href="37.htm#0">37</a> 
<a href="38.htm#0">38</a> 
<a href="39.htm#0">39</a> 
<a href="40.htm#0">40</a> 
<a href="41.htm#0">41</a> 
<a href="42.htm#0">42</a> 
<a href="43.htm#0">43</a> 
<a href="44.htm#0">44</a> 
<a href="45.htm#0">45</a> 
<a href="46.htm#0">46</a> 
<a href="47.htm#0">47</a> 
<a href="48.htm#0">48</a> 
<a href="49.htm#0">49</a> 
<a href="50.htm#0">50</a> 
<!--end of chapters-->
</p>
</div>
<div class="textAudio ym-noprint"><ul class="playlist">
    <li class="noMargin">
<!--start audio link--><a href="http://audio2.wordproject.com/bibles/app/audio/1/1/1.mp3">Genesis - Chapter 1 </a></li><!--/audioRef-->
    </ul>
  </div>

  <!--end audio-->
  <hr />
<div class="textBody" id="textBody"> 
  <h3>Chapter 1</h3>

<!--... the Word of God:--></a>
  <p><span class="verse" id="1">1</span> In the beginning God created the heaven and the earth. 
<br /><span class="verse" id="2">2</span> And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters. 
<br /><span class="verse" id="3">3</span> And God said, Let there be light: and there was light. 
<br /><span class="verse" id="4">4</span> And God saw the light, that it was good: and God divided the light from the darkness. 
<br /><span class="verse" id="5">5</span> And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day.  
<br /><span class="verse" id="6">6</span> And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters. 
<br /><span class="verse" id="7">7</span> And God made the firmament, and divided the waters which were under the firmament from the waters which were above the firmament: and it was so. 
<br /><span class="verse" id="8">8</span> And God called the firmament Heaven. And the evening and the morning were the second day. 
<br /><span class="verse" id="9">9</span> And God said, Let the waters under the heaven be gathered together unto one place, and let the dry land appear: and it was so. 
<br /><span class="verse" id="10">10</span> And God called the dry land Earth; and the gathering together of the waters called he Seas: and God saw that it was good. 
<br /><span class="verse" id="11">11</span> And God said, Let the earth bring forth grass, the herb yielding seed, and the fruit tree yielding fruit after his kind, whose seed is in itself, upon the earth: and it was so. 
<br /><span class="verse" id="12">12</span> And the earth brought forth grass, and herb yielding seed after his kind, and the tree yielding fruit, whose seed was in itself, after his kind: and God saw that it was good. 
<br /><span class="verse" id="13">13</span> And the evening and the morning were the third day. 
<br /><span class="verse" id="14">14</span> And God said, Let there be lights in the firmament of the heaven to divide the day from the night; and let them be for signs, and for seasons, and for days, and years: 
<br /><span class="verse" id="15">15</span> And let them be for lights in the firmament of the heaven to give light upon the earth: and it was so. 
<br /><span class="verse" id="16">16</span> And God made two great lights; the greater light to rule the day, and the lesser light to rule the night: he made the stars also. 
<br /><span class="verse" id="17">17</span> And God set them in the firmament of the heaven to give light upon the earth, 
<br /><span class="verse" id="18">18</span> And to rule over the day and over the night, and to divide the light from the darkness: and God saw that it was good. 
<br /><span class="verse" id="19">19</span> And the evening and the morning were the fourth day.  
<br /><span class="verse" id="20">20</span> And God said, Let the waters bring forth abundantly the moving creature that hath life, and fowl that may fly above the earth in the open firmament of heaven. 
<br /><span class="verse" id="21">21</span> And God created great whales, and every living creature that moveth, which the waters brought forth abundantly, after their kind, and every winged fowl after his kind: and God saw that it was good. 
<br /><span class="verse" id="22">22</span> And God blessed them, saying, Be fruitful, and multiply, and fill the waters in the seas, and let fowl multiply in the earth. 
<br /><span class="verse" id="23">23</span> And the evening and the morning were the fifth day. 
<br /><span class="verse" id="24">24</span> And God said, Let the earth bring forth the living creature after his kind, cattle, and creeping thing, and beast of the earth after his kind: and it was so. 
<br /><span class="verse" id="25">25</span> And God made the beast of the earth after his kind, and cattle after their kind, and every thing that creepeth upon the earth after his kind: and God saw that it was good. 
<br /><span class="verse" id="26">26</span> And God said, Let us make man in our image, after our likeness: and let them have dominion over the fish of the sea, and over the fowl of the air, and over the cattle, and over all the earth, and over every creeping thing that creepeth upon the earth. 
<br /><span class="verse" id="27">27</span> So God created man in his own image, in the image of God created he him; male and female created he them. 
<br /><span class="verse" id="28">28</span> And God blessed them, and God said unto them, Be fruitful, and multiply, and replenish the earth, and subdue it: and have dominion over the fish of the sea, and over the fowl of the air, and over every living thing that moveth upon the earth. 
<br /><span class="verse" id="29">29</span> And God said, Behold, I have given you every herb bearing seed, which is upon the face of all the earth, and every tree, in the which is the fruit of a tree yielding seed; to you it shall be for meat. 
<br /><span class="verse" id="30">30</span> And to every beast of the earth, and to every fowl of the air, and to every thing that creepeth upon the earth, wherein there is life, I have given every green herb for meat: and it was so. 
<br /><span class="verse" id="31">31</span> And God saw every thing that he had made, and, behold, it was very good. And the evening and the morning were the sixth day. 
</p>
<!--... sharper than any twoedged sword... -->
</div>
</div><!-- ym-wbox end -->
</div><!-- ym-wrapper end -->
</div><!-- ym-wrapper end -->
</div><!-- ym-wrapper end -->
<!--..sharper than any twoedged sword...-->
<div class="ym-wrapper">
    	<div class="ym-wbox">
<div class="alignRight ym-noprint">
  <p><a title="Print this page" href="javascript:window.print()" class="ym-button">&nbsp;<img src="../_assets/img/printer.gif" alt="printer" width="25" height="25" align="absbottom" />&nbsp;</a> 
    <a class="ym-button" title="Page TOP" href="#mytop">&nbsp;<img src="../_assets/img/arrow_up.png" alt="arrowup" width="25" height="25" align="absbottom" />&nbsp;</a> 
	<!--next chapter start-->
	<a class="ym-button" title="Next chapter" href="2.htm#0">&nbsp;<img src="../_assets/img/arrow_right.png" alt="arrowright" align="absbottom" />&nbsp;</a></p>
	<!--next chapter end-->
	</div>
</div>
</div>
<footer>
	<div class="ym-wrapper">
		<div class="ym-wbox">
			<p class="alignCenter">Wordproject® is a registered name of the <a href="http://www.wordproject.org">International Biblical Association</a>, a non-profit organization registered in Macau, China.	</p>
			<p class="alignCenter"><a href="http://www.wordproject.org/contact/new/index.htm" target="_top">Contact</a> | <a href="http://www.wordproject.org/contact/new/disclaim.htm" target="_top"> Disclaimer</a> | 
			<a href="http://www.wordproject.org/contact/new/state.htm" target="_top">Statement of Faith</a> | 
			<a href="http://www.wordproject.org/contact/new/mstate.htm" target="_top">Mission</a> | 
			<a href="http://www.wordproject.org/contact/new/copyrights.htm" target="_top">Copyrights</a></p>
		</div>
	</div>
</footer>
</body>
</script><script type="text/javascript" src="../_assets/js/jquery-1.8.0.min.js"></script>
<script type="text/javascript" src="../_assets/js/soundmanager2.js"></script>
<script type="text/javascript" src="../_assets/js/page-player.js"></script>
<script type="text/javascript" src="../_assets/js/script.js"></script>
<script type="text/javascript">

soundManager.setup({
  url: '../_assets/swf/'
});

</script>
</html>
"""


class TestWordProjectImport(TestCase):
    """
    Test the functions in the :mod:`wordprojectimport` module.
    """

    def setUp(self):
        self.registry_patcher = patch('openlp.plugins.bibles.lib.bibleimport.Registry')
        self.addCleanup(self.registry_patcher.stop)
        self.registry_patcher.start()
        self.manager_patcher = patch('openlp.plugins.bibles.lib.db.Manager')
        self.addCleanup(self.manager_patcher.stop)
        self.manager_patcher.start()

    @patch('openlp.plugins.bibles.lib.importers.wordproject.os')
    @patch('openlp.plugins.bibles.lib.importers.wordproject.copen')
    def test_process_books(self, mocked_open, mocked_os):
        """
        Test the process_books() method
        """
        # GIVEN: A WordProject importer and a bunch of mocked things
        importer = WordProjectBible(MagicMock(), path='.', name='.', filename='kj.zip')
        importer.base_dir = ''
        importer.stop_import_flag = False
        importer.language_id = 'en'
        mocked_open.return_value.__enter__.return_value.read.return_value = INDEX_PAGE
        mocked_os.path.join.side_effect = lambda *x: ''.join(x)

        # WHEN: process_books() is called
        with patch.object(importer, 'find_and_create_book') as mocked_find_and_create_book, \
                patch.object(importer, 'process_chapters') as mocked_process_chapters, \
                patch.object(importer, 'session') as mocked_session:
            importer.process_books()

        # THEN: The right methods should have been called
        mocked_os.path.join.assert_called_once_with('', 'index.htm')
        mocked_open.assert_called_once_with('index.htm', encoding='utf-8', errors='ignore')
        assert mocked_find_and_create_book.call_count == 66, 'There should be 66 books'
        assert mocked_process_chapters.call_count == 66, 'There should be 66 books'
        assert mocked_session.commit.call_count == 66, 'There should be 66 books'

    @patch('openlp.plugins.bibles.lib.importers.wordproject.os')
    @patch('openlp.plugins.bibles.lib.importers.wordproject.copen')
    def test_process_chapters(self, mocked_open, mocked_os):
        """
        Test the process_chapters() method
        """
        # GIVEN: A WordProject importer and a bunch of mocked things
        importer = WordProjectBible(MagicMock(), path='.', name='.', filename='kj.zip')
        importer.base_dir = ''
        importer.stop_import_flag = False
        importer.language_id = 'en'
        mocked_open.return_value.__enter__.return_value.read.return_value = CHAPTER_PAGE
        mocked_os.path.join.side_effect = lambda *x: ''.join(x)
        mocked_os.path.normpath.side_effect = lambda x: x
        mocked_db_book = MagicMock()
        mocked_db_book.name = 'Genesis'
        book_id = 1
        book_link = '01/1.htm'

        # WHEN: process_chapters() is called
        with patch.object(importer, 'set_current_chapter') as mocked_set_current_chapter, \
                patch.object(importer, 'process_verses') as mocked_process_verses:
            importer.process_chapters(mocked_db_book, book_id, book_link)

        # THEN: The right methods should have been called
        expected_set_current_chapter_calls = [call('Genesis', ch) for ch in range(1, 51)]
        expected_process_verses_calls = [call(mocked_db_book, 1, ch) for ch in range(1, 51)]
        mocked_os.path.join.assert_called_once_with('', '01/1.htm')
        mocked_open.assert_called_once_with('01/1.htm', encoding='utf-8', errors='ignore')
        assert mocked_set_current_chapter.call_args_list == expected_set_current_chapter_calls
        assert mocked_process_verses.call_args_list == expected_process_verses_calls

    @patch('openlp.plugins.bibles.lib.importers.wordproject.os')
    @patch('openlp.plugins.bibles.lib.importers.wordproject.copen')
    def test_process_verses(self, mocked_open, mocked_os):
        """
        Test the process_verses() method
        """
        # GIVEN: A WordProject importer and a bunch of mocked things
        importer = WordProjectBible(MagicMock(), path='.', name='.', filename='kj.zip')
        importer.base_dir = ''
        importer.stop_import_flag = False
        importer.language_id = 'en'
        mocked_open.return_value.__enter__.return_value.read.return_value = CHAPTER_PAGE
        mocked_os.path.join.side_effect = lambda *x: '/'.join(x)
        mocked_db_book = MagicMock()
        mocked_db_book.name = 'Genesis'
        book_number = 1
        chapter_number = 1

        # WHEN: process_verses() is called
        with patch.object(importer, 'process_verse') as mocked_process_verse:
            importer.process_verses(mocked_db_book, book_number, chapter_number)

        # THEN: All the right methods should have been called
        mocked_os.path.join.assert_called_once_with('', '01', '1.htm')
        mocked_open.assert_called_once_with('/01/1.htm', encoding='utf-8', errors='ignore')
        assert mocked_process_verse.call_count == 31

    def test_process_verse(self):
        """
        Test the process_verse() method
        """
        # GIVEN: An importer and a mocked method
        importer = WordProjectBible(MagicMock(), path='.', name='.', filename='kj.zip')
        mocked_db_book = MagicMock()
        mocked_db_book.id = 1
        chapter_number = 1
        verse_number = 1
        verse_text = '  In the beginning, God created the heavens and the earth   '

        # WHEN: process_verse() is called
        with patch.object(importer, 'create_verse') as mocked_create_verse:
            importer.process_verse(mocked_db_book, chapter_number, verse_number, verse_text)

        # THEN: The create_verse() method should have been called
        mocked_create_verse.assert_called_once_with(1, 1, 1, 'In the beginning, God created the heavens and the earth')

    def test_process_verse_no_text(self):
        """
        Test the process_verse() method when there's no text
        """
        # GIVEN: An importer and a mocked method
        importer = WordProjectBible(MagicMock(), path='.', name='.', filename='kj.zip')
        mocked_db_book = MagicMock()
        mocked_db_book.id = 1
        chapter_number = 1
        verse_number = 1
        verse_text = ''

        # WHEN: process_verse() is called
        with patch.object(importer, 'create_verse') as mocked_create_verse:
            importer.process_verse(mocked_db_book, chapter_number, verse_number, verse_text)

        # THEN: The create_verse() method should NOT have been called
        assert mocked_create_verse.call_count == 0

    def test_do_import(self):
        """
        Test the do_import() method
        """
        # GIVEN: An importer and mocked methods
        importer = WordProjectBible(MagicMock(), path='.', name='.', filename='kj.zip')

        # WHEN: do_import() is called
        with patch.object(importer, '_unzip_file') as mocked_unzip_file, \
                patch.object(importer, 'get_language_id') as mocked_get_language_id, \
                patch.object(importer, 'process_books') as mocked_process_books, \
                patch.object(importer, '_cleanup') as mocked_cleanup:
            mocked_get_language_id.return_value = 1
            result = importer.do_import()

        # THEN: The correct methods should have been called
        mocked_unzip_file.assert_called_once_with()
        mocked_get_language_id.assert_called_once_with(None, bible_name='kj.zip')
        mocked_process_books.assert_called_once_with()
        mocked_cleanup.assert_called_once_with()
        assert result is True

    def test_do_import_no_language(self):
        """
        Test the do_import() method when the language is not available
        """
        # GIVEN: An importer and mocked methods
        importer = WordProjectBible(MagicMock(), path='.', name='.', filename='kj.zip')

        # WHEN: do_import() is called
        with patch.object(importer, '_unzip_file') as mocked_unzip_file, \
                patch.object(importer, 'get_language_id') as mocked_get_language_id, \
                patch.object(importer, 'process_books') as mocked_process_books, \
                patch.object(importer, '_cleanup') as mocked_cleanup:
            mocked_get_language_id.return_value = None
            result = importer.do_import()

        # THEN: The correct methods should have been called
        mocked_unzip_file.assert_called_once_with()
        mocked_get_language_id.assert_called_once_with(None, bible_name='kj.zip')
        assert mocked_process_books.call_count == 0
        mocked_cleanup.assert_called_once_with()
        assert result is False
