<!DOCTYPE html>
<html>
<!--
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
-->
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, minimum-scale=1, maximum-scale=1" />
  <title>${app_title}</title>
  <link rel="stylesheet" href="/static/assets/jquery.mobile.min.css" />
  <link rel="stylesheet" href="/static/css/openlp.css" />
  <link rel="shortcut icon" type="image/x-icon" href="/static/images/favicon.ico">
  <script type="text/javascript" src="/static/assets/jquery.min.js"></script>
  <script type="text/javascript" src="/static/js/openlp.js"></script>
  <script type="text/javascript" src="/static/assets/jquery.mobile.min.js"></script>
  <script type="text/javascript">
  translationStrings = {
    "go_live": "${go_live}",
    "add_to_service": "${add_to_service}",
    "no_results": "${no_results}",
    "home": "${home}"
  }
  </script>
</head>
<body>
<div data-role="page" id="home">
  <div data-role="header">
    <h1>${app_title}</h1>
  </div>
  <div data-role="content">
    <div data-role="controlgroup">
      <a href="#service-manager" data-role="button" data-icon="arrow-r" data-iconpos="right">${service_manager}</a>
      <a href="#slide-controller" data-role="button" data-icon="arrow-r" data-iconpos="right">${slide_controller}</a>
      <a href="#alerts" data-role="button" data-icon="arrow-r" data-iconpos="right">${alerts}</a>
      <a href="#search" data-role="button" data-icon="arrow-r" data-iconpos="right">${search}</a>
    </div>
  </div>
</div>
<div data-role="page" id="service-manager">
  <div data-role="header" data-position="fixed">
    <a href="#home" data-role="button" data-icon="home" data-iconpos="left">${home}</a>
    <h1>${service_manager}</h1>
    <a href="#" id="service-refresh" data-role="button" data-icon="refresh">${refresh}</a>
    <div data-role="navbar">
      <ul>
        <li><a href="#service-manager" data-theme="e">${service}</a></li>
        <li><a href="#slide-controller">${slides}</a></li>
        <li><a href="#alerts">${alerts}</a></li>
        <li><a href="#search">${search}</a></li>
      </ul>
    </div>
  </div>
  <div data-role="content">
    <ul data-role="listview" data-inset="true">
    </ul>
  </div>
  <div data-role="footer" data-theme="b" class="ui-bar" data-position="fixed">
    <div data-role="controlgroup" data-type="horizontal" style="float: left;">
      <a href="#" id="service-blank" data-role="button" data-icon="blank">${blank}</a>
      <a href="#" id="service-theme" data-role="button">${theme}</a>
      <a href="#" id="service-desktop" data-role="button">${desktop}</a>
      <a href="#" id="service-show" data-role="button" data-icon="unblank" data-iconpos="right">${show}</a>
    </div>
    <div data-role="controlgroup" data-type="horizontal" style="float: left;">
      <a href="#" id="service-previous" data-role="button" data-icon="arrow-l">${prev}</a>
      <a href="#" id="service-next" data-role="button" data-icon="arrow-r" data-iconpos="right">${next}</a>
    </div>
  </div>
</div>
<div data-role="page" id="slide-controller">
  <div data-role="header" data-position="fixed">
    <a href="#home" data-role="button" data-icon="home" data-iconpos="left">${home}</a>
    <h1>${slide_controller}</h1>
    <a href="#" id="controller-refresh" data-role="button" data-icon="refresh">${refresh}</a>
    <div data-role="navbar">
      <ul>
        <li><a href="#service-manager">${service}</a></li>
        <li><a href="#slide-controller" data-theme="e">${slides}</a></li>
        <li><a href="#alerts">${alerts}</a></li>
        <li><a href="#search">${search}</a></li>
      </ul>
    </div>
  </div>
  <div data-role="content">
    <ul data-role="listview" data-inset="true">
    </ul>
  </div>
  <div data-role="footer" data-theme="b" class="ui-bar" data-position="fixed">
    <div data-role="controlgroup" data-type="horizontal" style="float: left;">
      <a href="#" id="controller-blank" data-role="button" data-icon="blank">${blank}</a>
      <a href="#" id="controller-theme" data-role="button">${theme}</a>
      <a href="#" id="controller-desktop" data-role="button">${desktop}</a>
      <a href="#" id="controller-show" data-role="button" data-icon="unblank" data-iconpos="right">${show}</a>
    </div>
    <div data-role="controlgroup" data-type="horizontal" style="float: left;">
      <a href="#" id="controller-previous" data-role="button" data-icon="arrow-l">${prev}</a>
      <a href="#" id="controller-next" data-role="button" data-icon="arrow-r" data-iconpos="right">${next}</a>
    </div>
  </div>
</div>
<div data-role="page" id="alerts">
  <div data-role="header">
    <a href="#home" data-role="button" data-icon="home" data-iconpos="left">${home}</a>
    <h1>${alerts}</h1>
    <div data-role="navbar">
      <ul>
        <li><a href="#service-manager">${service}</a></li>
        <li><a href="#slide-controller">${slides}</a></li>
        <li><a href="#alerts" data-theme="e">${alerts}</a></li>
        <li><a href="#search">${search}</a></li>
      </ul>
    </div>
  </div>
  <div data-role="content">
    <div data-role="fieldcontain">
      <label for="alert-text">${text}:</label>
      <input type="text" name="alert-text" id="alert-text" value="" />
    </div>
    <a href="#" id="alert-submit" data-role="button">${show_alert}</a>
  </div>
</div>
<div data-role="page" id="search">
  <div data-role="header" data-position="fixed">
    <a href="#home" data-role="button" data-icon="home" data-iconpos="left">${home}</a>
    <h1>${search}</h1>
    <div data-role="navbar">
      <ul>
        <li><a href="#service-manager">${service}</a></li>
        <li><a href="#slide-controller">${slides}</a></li>
        <li><a href="#alerts">${alerts}</a></li>
        <li><a href="#search" data-theme="e">${search}</a></li>
      </ul>
    </div>
  </div>
  <div data-role="content">
    <div data-role="fieldcontain">
      <label for="search-plugin">${search}:</label>
      <select name="search-plugin" id="search-plugin" data-native-menu="false"></select>
    </div>
    <div data-role="fieldcontain">
      <label for="search-text">${text}:</label>
      <input type="search" name="search-text" id="search-text" value="" />
    </div>
    <a href="#" id="search-submit" data-role="button">${search}</a>
    <ul data-role="listview" data-inset="true"/>
  </div>
</div>
<div data-role="page" id="options">
  <div data-role="header" data-position="inline" data-theme="b">
    <h1>${options}</h1>
  </div>
  <div data-role="content">
    <input type="hidden" id="selected-item" value="" />
    <a href="#" id="go-live" data-role="button">${go_live}</a>
    <a href="#" id="add-to-service" data-role="button">${add_to_service}</a>
    <a href="#" id="add-and-go-to-service" data-role="button">${add_and_go_to_service}</a>
  </div>
</div>
</body>
</html>
