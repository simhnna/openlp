/******************************************************************************
 * OpenLP - Open Source Lyrics Projection                                      *
 * --------------------------------------------------------------------------- *
 * Copyright (c) 2008-2016 OpenLP Developers                                   *
 * --------------------------------------------------------------------------- *
 * This program is free software; you can redistribute it and/or modify it     *
 * under the terms of the GNU General Public License as published by the Free  *
 * Software Foundation; version 2 of the License.                              *
 *                                                                             *
 * This program is distributed in the hope that it will be useful, but WITHOUT *
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    *
 * more details.                                                               *
 *                                                                             *
 * You should have received a copy of the GNU General Public License along     *
 * with this program; if not, write to the Free Software Foundation, Inc., 59  *
 * Temple Place, Suite 330, Boston, MA 02111-1307 USA                          *
 ******************************************************************************/
window.OpenLP = {
  loadSlide: function (event) {
    $.getJSON(
      "/main/image",
      function (data, status) {
        var img = document.getElementById('image');
        img.src = data.results.slide_image;
        img.style.display = 'block';
      }
    );
  },
  pollServer: function () {
    if ("WebSocket" in window) {
        // Let us open a web socket
        var ws = new WebSocket('ws://' + location.hostname + ':4317/live_changed');
        ws.binaryType = 'arraybuffer';
        ws.onmessage = function (evt) {
            var msg = JSON.parse(String.fromCharCode.apply(null, new Uint8Array(evt.data)));
            if (OpenLP.slideCount != msg.results.slide_count) {
              OpenLP.slideCount = msg.results.slide_count;
              OpenLP.loadSlide();
            }
        }
    } else {
        // The browser doesn't support WebSocket
        alert("WebSocket NOT supported by your Browser!");
    }      
  }
};
$.ajaxSetup({ cache: false });
OpenLP.pollServer();

