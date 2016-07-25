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
var lastChord;

var notesSharpNotation = {}
var notesFlatNotation = {}

// See https://en.wikipedia.org/wiki/Musical_note#12-tone_chromatic_scale
notesSharpNotation['german'] = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','H'];
notesFlatNotation['german'] = ['C','Db','D','Eb','Fb','F','Gb','G','Ab','A','B','H'];
notesSharpNotation['english'] = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
notesFlatNotation['english'] = ['C','Db','D','Eb','Fb','F','Gb','G','Ab','A','Bb','B'];
notesSharpNotation['neo-latin'] = ['Do','Do#','Re','Re#','Mi','Fa','Fa#','Sol','Sol#','La','La#','Si'];
notesFlatNotation['neo-latin'] = ['Do','Reb','Re','Mib','Fab','Fa','Solb','Sol','Lab','La','Sib','Si'];

function getTransposeValue(songId) {
  if (localStorage.getItem(songId + '_transposeValue')) {return localStorage.getItem(songId + '_transposeValue');}
  else {return 0;}
}

function storeTransposeValue(songId,transposeValueToSet) {
  localStorage.setItem(songId + '_transposeValue', transposeValueToSet);
}

// NOTE: This function has a python equivalent in openlp/plugins/songs/lib/__init__.py - make sure to update both!
function transposeChord(chord, transposeValue, notation) {
  var chordSplit = chord.replace('♭', 'b').split(/[\/\(\)]/);
  var transposedChord = '', note, notenumber, rest, currentChord;
  var notesSharp = notesSharpNotation[notation];
  var notesFlat = notesFlatNotation[notation];
  var notesPreferred = ['b','#','#','#','#','#','#','#','#','#','#','#'];
  var chordNotes = Array();
  for (i = 0; i <= chordSplit.length - 1; i++) {
    if (i > 0) {
      transposedChord += '/';
    }
    currentchord = chordSplit[i];
    if (currentchord.charAt(0) === '(') {
      transposedChord += '(';
      if (currentchord.length > 1) {
        currentchord = currentchord.substr(1);
      } else {
        currentchord = "";
      }
    }
    if (currentchord.length > 0) {
      if (currentchord.length > 1) {
        if ('#b'.indexOf(currentchord.charAt(1)) === -1) {
          note = currentchord.substr(0, 1);
          rest = currentchord.substr(1);
        } else {
          note = currentchord.substr(0, 2);
          rest = currentchord.substr(2);
        }
      } else {
        note = currentchord;
        rest = "";
      }
      notenumber = (notesSharp.indexOf(note) === -1 ? notesFlat.indexOf(note) : notesSharp.indexOf(note));
      notenumber -= parseInt(transposeValue);
      while (notenumber > 11) {
        notenumber -= 12;
      }
      while (notenumber < 0) {
        notenumber += 12;
      }
      if (i === 0) {
        currentChord = notesPreferred[notenumber] === '#' ? notesSharp[notenumber] : notesFlat[notenumber];
        lastChord = currentChord;
      } else {
        currentChord = notesSharp.indexOf(lastChord) === -1 ? notesFlat[notenumber] : notesSharp[notenumber];
      }
      if (!(notesFlat.indexOf(note) === -1 && notesSharp.indexOf(note) === -1)) {
        transposedChord += currentChord + rest;
      } else {
        transposedChord += note + rest;
      }
    }
  }
  return transposedChord;
}

var OpenLPChordOverflowFillCount = 0;
window.OpenLP = {
  showchords:true,
  loadService: function (event) {
    $.getJSON(
      "/api/service/list",
      function (data, status) {
        OpenLP.nextSong = "";
        $("#notes").html("");
        for (idx in data.results.items) {
          idx = parseInt(idx, 10);
          if (data.results.items[idx]["selected"]) {
            $("#notes").html(data.results.items[idx]["notes"].replace(/\n/g, "<br />"));
            if (data.results.items.length > idx + 1) {
              OpenLP.nextSong = data.results.items[idx + 1]["title"];
            }
            break;
          }
        }
        OpenLP.updateSlide();
      }
    );
  },
  loadSlides: function (event) {
    $.getJSON(
      "/api/controller/live/text",
      function (data, status) {
        OpenLP.currentSlides = data.results.slides;
        $('#transposevalue').text(getTransposeValue(OpenLP.currentSlides[0].text.split("\n")[0]));
        OpenLP.currentSlide = 0;
        OpenLP.currentTags = Array();
        var div = $("#verseorder");
        div.html("");
        var tag = "";
        var tags = 0;
        var lastChange = 0;
        $.each(data.results.slides, function(idx, slide) {
          var prevtag = tag;
          tag = slide["tag"];
          if (tag != prevtag) {
            // If the tag has changed, add new one to the list
            lastChange = idx;
            tags = tags + 1;
            div.append("&nbsp;<span>");
            $("#verseorder span").last().attr("id", "tag" + tags).text(tag);
          }
          else {
            if ((slide["chords_text"] == data.results.slides[lastChange]["chords_text"]) &&
              (data.results.slides.length > idx + (idx - lastChange))) {
              // If the tag hasn't changed, check to see if the same verse
              // has been repeated consecutively. Note the verse may have been
              // split over several slides, so search through. If so, repeat the tag.
              var match = true;
              for (var idx2 = 0; idx2 < idx - lastChange; idx2++) {
                if(data.results.slides[lastChange + idx2]["chords_text"] != data.results.slides[idx + idx2]["chords_text"]) {
                    match = false;
                    break;
                }
              }
              if (match) {
                lastChange = idx;
                tags = tags + 1;
                div.append("&nbsp;<span>");
                $("#verseorder span").last().attr("id", "tag" + tags).text(tag);
              }
            }
          }
          OpenLP.currentTags[idx] = tags;
          if (slide["selected"])
            OpenLP.currentSlide = idx;
        })
        OpenLP.loadService();
      }
    );
  },
  updateSlide: function() {
    // Show the current slide on top. Any trailing slides for the same verse
    // are shown too underneath in grey.
    // Then leave a blank line between following verses
    var transposeValue = getTransposeValue(OpenLP.currentSlides[0].text.split("\n")[0]);
    var chordclass=/class="[a-z\s]*chord[a-z\s]*"\s*style="display:\s?none"/g;
    var chordclassshow='class="chord"';
    var regchord=/<span class="chord"><span><strong>([\(\w#b♭\+\*\d/\)-]+)<\/strong><\/span><\/span>([\u0080-\uFFFF,\w]*)(<span class="ws">.+?<\/span>)?([\u0080-\uFFFF,\w,\s,\.,\,,\!,\?,\;,\:,\|,\",\',\-,\_]*)(<br>)?/g;
    // NOTE: There is equivalent python code in openlp/core/lib/__init__.py, in the expand_and_align_chords_in_line function. Make sure to update both!
    var replaceChords=function(mstr,$chord,$tail,$skips,$remainder,$end) {
      var v='';
      var w='';
      var $chordlen = 0;
      var $taillen = 0;
      var slimchars='fiíIÍjlĺľrtť.,;/ ()|"\'!:\\';
      // Transpose chord as dictated by the transpose value in local storage
      $chord = transposeChord($chord, transposeValue, OpenLP.chordNotation);
      // Replace any padding '_' added to tail
      $tail = $tail.replace(/_+$/, '')
      console.log('chord: ' +$chord +', tail: ' + $tail + ', remainder: ' + $remainder +', end: ' + $end +', match: ' + mstr)
      for (var i = 0; i < $chord.length; i++) if (slimchars.indexOf($chord.charAt(i)) === -1) {$chordlen += 2;} else {$chordlen += 1;}
      for (var i = 0; i < $tail.length; i++) if (slimchars.indexOf($tail.charAt(i)) === -1) {$taillen += 2;} else {$taillen += 1;}
      for (var i = 0; i < $remainder.length; i++) if (slimchars.indexOf($tail.charAt(i)) === -1) {$taillen += 2;} else {$taillen += 1;}
      if ($chordlen >= $taillen && !$end) {
        if ($tail.length){
          if (!$remainder.length) {
            for (c = 0; c < Math.ceil(($chordlen - $taillen) / 2) + 1; c++) {w += '_';}
          } else {
            for (c = 0; c < $chordlen - $taillen + 2; c++) {w += '&nbsp;';}
          }
        } else {
          if (!$remainder.length) {
            for (c = 0; c < Math.floor(($chordlen - $taillen) / 2) + 1; c++) {w += '_';}
          } else {
            for (c = 0; c < $chordlen - $taillen + 1; c++) {w += '&nbsp;';}
          }
        };
      } else {
        if (!$tail && $remainder.charAt(0) == ' ') {for (c = 0; c < $chordlen; c++) {w += '&nbsp;';}}
      }
      if (w!='') {
        w='<span class="ws">' + w + '</span>';
      }
      return $.grep(['<span class="chord"><span><strong>', $chord, '</strong></span></span>', $tail, w, $remainder, $end], Boolean).join('');
    };
    $("#verseorder span").removeClass("currenttag");
    $("#tag" + OpenLP.currentTags[OpenLP.currentSlide]).addClass("currenttag");
    var slide = OpenLP.currentSlides[OpenLP.currentSlide];
    var text = "";
    // use title if available
    if (slide["title"]) {
        text = slide["title"];
    } else {
        text = slide["chords_text"];
        if(OpenLP.showchords) {
            text = text.replace(chordclass,chordclassshow);
            text = text.replace(regchord, replaceChords);
        }
    }
    // use thumbnail if available
    if (slide["img"]) {
        text += "<br /><img src='" + slide["img"].replace("/thumbnails/", "/thumbnails320x240/") + "'><br />";
    }
    // use notes if available
    if (slide["slide_notes"]) {
        text += '<br />' + slide["slide_notes"];
    }
    text = text.replace(/\n/g, "<br />");
    $("#currentslide").html(text);
    text = "";
    if (OpenLP.currentSlide < OpenLP.currentSlides.length - 1) {
      for (var idx = OpenLP.currentSlide + 1; idx < OpenLP.currentSlides.length; idx++) {
        if (OpenLP.currentTags[idx] != OpenLP.currentTags[idx - 1])
            text = text + "<p class=\"nextslide\">";
        if (OpenLP.currentSlides[idx]["title"]) {
            text = text + OpenLP.currentSlides[idx]["title"];
        } else {
            text = text + OpenLP.currentSlides[idx]["chords_text"];
            if(OpenLP.showchords) {
              text = text.replace(chordclass,chordclassshow);
              text = text.replace(regchord, replaceChords);
            }
        }
        if (OpenLP.currentTags[idx] != OpenLP.currentTags[idx - 1])
            text = text + "</p>";
        else
            text = text + "<br />";
      }
      text = text.replace(/\n/g, "<br />");
      $("#nextslide").html(text);
      $("#nextslide").class("nextslide");
    }
    else {
      text = "<p class=\"nextslide\">" + $("#next-text").val() + ": " + OpenLP.nextSong + "</p>";
      $("#nextslide").html(text);
    }
  if(!OpenLP.showchords) $(".chordline").toggleClass('chordline1');
  },
  updateClock: function(data) {
    var div = $("#clock");
    var t = new Date();
    var h = t.getHours();
    if (data.results.twelve && h > 12)
      h = h - 12;
  if (h < 10) h = '0' + h + '';
    var m = t.getMinutes();
    if (m < 10)
      m = '0' + m + '';
    div.html(h + ":" + m);
  },
  pollServer: function () {
    $.getJSON(
      "/api/poll",
      function (data, status) {
        OpenLP.updateClock(data);
        OpenLP.chordNotation = data.results.chordNotation;
        if (OpenLP.currentItem != data.results.item || OpenLP.currentService != data.results.service) {
          OpenLP.currentItem = data.results.item;
          OpenLP.currentService = data.results.service;
          OpenLP.loadSlides();
        }
        else if (OpenLP.currentSlide != data.results.slide) {
          OpenLP.currentSlide = parseInt(data.results.slide, 10);
          OpenLP.updateSlide();
        }
      }
    );
  }
}
$.ajaxSetup({ cache: false });
setInterval("OpenLP.pollServer();", 500);
OpenLP.pollServer();
$(document).ready(function() {
  $('#transposeup').click(function(e) {
    $('#transposevalue').text(parseInt($('#transposevalue').text()) + 1);
    storeTransposeValue(OpenLP.currentSlides[0].text.split("\n")[0], $('#transposevalue').text());
    OpenLP.loadSlides();
  });
  $('#transposedown').click(function(e) {  
    $('#transposevalue').text(parseInt($('#transposevalue').text()) - 1);
    storeTransposeValue(OpenLP.currentSlides[0].text.split("\n")[0], $('#transposevalue').text());
    OpenLP.loadSlides();
  });
});
