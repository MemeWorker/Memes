
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
230
231
232
233
234
235
236
237
238
239
240
241
242
243
244
245
246
247
248
249
250
251
252
253
254
255
256
257
258
259
260
261
262
263
264
265
266
267
268
269
270
271
272
273
274
275
276
277
278
279
280
281
282
283
284
285
286
287
288
289
290
291
292
293
294
295
296
297
298
299
300
301
302
303
304
305
306
307
308
309
310
311
312
313
314
315
316
317
318
319
320
321
322
323
324
325
326
327
328
329
330
331
332
333
334
335
336
337
338
339
340
341
342
343
344
345
346
347
348
349
350
351
352
353
354
355
356
357
358
359
360
361
362
363
364
365
366
367
368
369
370
371
372
373
374
375
376
377
378
379
380
381
382
383
384
385
386
387
388
389
390
391
392
393
// ==UserScript==
// @name        Razors Alis Hacks
// @version     6.6
// @description READ THIS SCRIPT BEFORE USING!
// @author      Razor
// @match       http://alis.io/*
// @match       http://d.alis.io/*
// @run-at      document-end
// @grant       GM_getResourceText
// @grant       GM_addStyle
// @grant       GM_xmlhttpRequest
// @grant       GM_getResourceURL
// @grant       GM_xmlhttpRequest
// @namespace https://greasyfork.org/users/81850
// ==/UserScript==

// define levels of hackery
var playerSettings = {
    "normal": {
        "speed": 50,
        "maxCells": 32,
        "maxSize": 15000000,
        "isToxic": 1,
        "ignoreBorders": 1,
        "decayRate": -0.002,
        "staticDecay": 0,
    },
    "slow": {
        "speed": 0.00001,
        "recombineTime": 0,
        "maxCells": 1,
        "maxSize": 1700,
        "decayRate": -0.0001,
        "staticDecay": 1,
        "isToxic": 0,
        "ignoreBorders": 1,
        "viewBaseX": 10000,
        "viewBaseY": 10000,
        "startMass": 4000,
    },
    "fast": {
        "speed": 10,
        "recombineTime": 0,
        "maxCells": 1,
        "maxSize": 7000,
        "decayRate": -0.02,
        "staticDecay": 1,
        "isToxic": 1,
        "ignoreBorders": 1,
        "viewBaseX": 10000,
        "viewBaseY": 10000,
        "startMass": 30000,
    }
};

/* Complete list of available per-player detail settings:
# grep -roP "playerDetails\..+(\s+)" . | cut -d ' ' -f 1 | grep -oP playerDetails.+ | tr -d ');,' | sort | uniq
playerDetails.decayModifier - internal game mode use, changes do nothing
playerDetails.decayRate - only used if staticDecay is 1. values from 0.9 (extremely fast decay) to -1 (extremely fast growth)
playerDetails.dynamicDecay - internal game use, changes do nothing
playerDetails.hasToxicWall - razors gayest invention yet
playerDetails.ignoreBorders - can go outside map borders
playerDetails.isAdmin - enables/disables the use of hacks
playerDetails.isToxic - makes players toxic feed shrink eaters
playerDetails.isTroll - only used pre-connect to determine trollability of player
playerDetails.maxCells - number of cells player can be split into
playerDetails.maxSize - max size in RADIUS of cell, not mass
playerDetails.nameColor - array of RGB colors, can not be altered in game
playerDetails.nameColor.b - blue
playerDetails.nameColor.g - green
playerDetails.nameColor.r - red
playerDetails.recombineTime - how quickly can this player recombine, 30 is slow, 0 is instant
playerDetails.scoreDivisor - internal only, changes do nothing.
ejectSize, ejectSizeLoss, ejectDistance all pretty self explanatory
playerDetails.speed - how fast is the player, 1 for normal, 10 for very fast
playerDetails.startMass - starting size in cell mass
playerDetails.startSize - starting size in cell radius
playerDetails.staticDecay - off by default, uses dynamic decay formula based on total server mass. 1 for enabled a constant decay rate
playerDetails.sub - SUBJECT of json web token, used to identify their account across games
playerDetails.totalScore - internal to track last total score of the player
playerDetails.validFrom - internal only used during connection and token vlidation
playerDetails.viewBaseX - 1920 default, 10000 for massive view
playerDetails.viewBaseY - 1080 default, 10000 for massive view
You can do /set playerID settingName newValue to alter an individual players value above
Or you can do /playerDetails playerID to see their current values for all of these in console
*/
/* List of server-wide changes:
Coming soon...
*/
// Counter to roll through levels of hackery (index = nextHack modulous hackCount)
var nextHack = 1;

// Mass toggle values
var massToggle = [2000,18000];
var nextMass = 1;

// Add the dom elements we want to display information in
$(function() {
    // Fix the max length for the skin url box
    $("#skinurl").attr('maxlength','600');
    // Add the hack div to the overlay2 div
    $('#overlays2').append('<div id="hackdiv" style="position: absolute; top: 40px; left: 19px; color: #fff;"></div>');
    // add player id, target id, status, and hotkeys to the hack div
    $('#hackdiv').append('Your Player ID: <span style="font-weight: bold;" id="yourplayerid"></span><br>');
    $('#hackdiv').append('Hack Target ID: <span style="font-weight: bold;" id="targetplayerid"></span><br>');
    $('#hackdiv').append('Status: <span style="font-weight: bold;" id="hackstatus"></span><br>');
    $('#hackdiv').append('<div id="hackkeys" style="font-size: 12px; line-height: 15px;"></div>');
    // add the hackkeys list to the hackkeys div
    $('#hackkeys').append('<b>Hotkeys:</b><ul id="hackkeylist" style="list-style: none; padding-left: 15px;"></ul>');
    // add each of the hotkeys to the hackkey list
    $('#hackkeylist').append('<li><b>LEFT CLICK</b> to target player</li>');
    //$('#hackkeylist').append('<li><b>MIDDLE CLICK</b> to target ALL OTHER players</li>');
    $('#hackkeylist').append('<li><b>1</b> toggle hacks low/medium/ghauf<br>');
    $('#hackkeylist').append('<li><b>2</b> teleport target(s) to mouse<br>');
    $('#hackkeylist').append('<li><b>3</b> toggle target(s) mass big/small<br>');
    $('#hackkeylist').append('<li><b>4</b> spawn virus at mouse<br>');
    $('#hackkeylist').append('<li><b>5</b> kill target(s)<br>');
    $('#hackkeylist').append('<li><b>/</b> send chat & commands</li>');
// make greeb sad
    $("iframe").remove();
    $("video").remove();
    $("#ad_main").remove();
});

// Wrapper to send commands
function sendHack(command) {
    //console.log('SENDING: ' + command);
    unsafeWindow.sendChat(command);
}

// Wrapper to send commands targeting to player(s)
function sendTargetHack(command, targets, params) {
    // If params is an array, join it with spaces
    if (Array.isArray(params)) {
        params = params.join(' ');
    }
    // if the targets are an array, send it to multiple targets
    if (Array.isArray(targets)) {
        for(var target in targets) {
            sendHack('/' + command + ' ' + targets[target] + ' ' + params);
        }
    } else {
        sendHack('/' + command + ' ' + targets + ' ' + params);
    }
}
unsafeWindow.sendHack = function (command, params) { sendTargetHack(command, JSON.parse($('#targetplayerid').html()), params); };

// helper for console fuckery
unsafeWindow.setAll = function(key, value) {
    // Get the json targets on our target player id list
    var targets = JSON.parse($('#targetplayerid').html());
    sendTargetHack('set', targets, [ key, value ]);
};

// Update our player ID every few seconds
var updateMyID = setInterval(function(){
    sendHack('/getmyid');
}, 10 * 1000);

// Keypress handler
function keydown(event) {
    //console.log(event); // for debugging
    // Do not process keypress events NOT on the body element itself
    if(event.target.nodeName != "BODY") {
       return;
    }
    var command = '';

    // if we dont know our player id, request it
    if (!$('#yourplayerid').html()) {
        sendHack('/getmyid');
    }

    // This is ` or ~ key
    if (event.keyCode == 192) {
        $('#hackstatus').html('Set target = self');
        $('#targetplayerid').html(JSON.stringify($('#yourplayerid').html()));
    }

    // if the target ID is not defined, no commands will work
    if (!$('#targetplayerid').html()) {
        $('#hackstatus').html('target not set');
        return;
    }

    // Get the json targets on our target player id list
    var targets = JSON.parse($('#targetplayerid').html());
    /*
    // IF the targets list is an array of players, make sure our id is not in the target list
    if (Array.isArray(targets)) {
        var myID = parseInt($('#yourplayerid').html());
        var myIndex = targets.indexOf(myID);
        if (myIndex) {
            targets.splice( myIndex, 1 );
        }
    }*/
    // This is 1 key, toggle between hacks
    if (event.keyCode == 49) {
        // calculate index of hacks to apply
        var hackIndex = nextHack % Object.keys(playerSettings).length;
        var hackKey = Object.keys(playerSettings)[hackIndex];
        var settings = playerSettings[hackKey];
        // apply hacks
        for (var k in settings) {
            sendTargetHack('set', targets, [ k, settings[k] ]);
        }
        // set next hack to the next index
        nextHack++;
        $('#hackstatus').html('set target hacks to: ' + hackKey);
    }

    // 2 key, teleport to mouse location
    if (event.keyCode == 50) {
        sendTargetHack('teleport', targets, [ mouseX, mouseY ]);
        $('#hackstatus').html('teleported target');
    }

    // 3 key, toggle mass hack 2k/18k
    if (event.keyCode == 51) {
        var massKey = nextMass % massToggle.length;
        sendTargetHack('mass', targets ,massToggle[massKey]);
        $('#hackstatus').html('mass set to ' + massToggle[massKey]);
        nextMass++;
    }

    // 4 key, spawns virus cluster at mouse location
    if (event.keyCode == 52) {
        var sizes = [100, 200, 300, 500, 700, 900, 1000, 1300, 1600, 1900, 2200, 2500, 2800, 3000, 3100];
        sizes.forEach(function(size) {
            command = "/virus " + mouseX + " " + mouseY + " " + size;
            sendHack(command);
        });
        $('#hackstatus').html('spawned virus cluster');
    }

    // 5 key, kill target(s)
    if (event.keyCode == 53) {
        sendTargetHack('kill', targets, '');
        $('#hackstatus').html('killed target player(s)');
        nextMass++;
    }
}

// Get target cell ID
function getClosestCellID(X, Y) {
    $('#hackstatus').html('searching for cell id near mouse ' + X + ',' + Y);
    var cells = unsafeWindow.allCells;

    // Loop through all the cells and extract JUST the players
    var playerCells = [];
    for (var i in cells) {
        var playerCell = cells[i];
        // Ignore food pellets & tiny cells
        if (playerCell.isFood || playerCell.size < 35) {
            continue;
        }
        // F is old agarplus obfuscated isVirus flag
        if (playerCell.f || playerCell.isVirus) {
            continue;
        }
        // Calculate the x and y distances
        var distx = playerCell.x - X;
        var disty = playerCell.y - Y;
        // calculates distance between two X,Y points
        var distance = Math.sqrt( Math.pow(distx, 2) + Math.pow(disty, 2) );
        // save our player cell info
        var razorCell = {};
        razorCell.id = i;
        razorCell.name = playerCell.name;
        razorCell.distance = distance;
        razorCell.size = playerCell.size;
        razorCell.x = playerCell.x;
        razorCell.y = playerCell.y;
        playerCells.push(razorCell);
    }
    // Sort the cells by distance ascending
    playerCells.sort(function (a, b) { return a.distance - b.distance; });
    //console.log('closest player identified: ');
    //console.table(playerCells.slice(0, 1));
    if (playerCells.length) {
        return playerCells[0].id;
    } else {
        return 0;
    }
}

// left Mouse click handler
function leftMouseClick()
{
    var cellid = getClosestCellID(mouseX, mouseY);
    if (cellid) {
        $('#hackstatus').html('requested player id of cell ' + cellid);
        var cell = unsafeWindow.allCells[cellid];
        if(cell.extra && cell.extra.pid) {
            $('#targetplayerid').html(JSON.stringify(cell.extra.pid));
            $('#hackstatus').html('target player switched to ' + $('#targetplayerid').html());
        } else {
            $('#hackstatus').html('unable to get player id of cell ' + cellid);
        }
    }else{
        $('#hackstatus').html('could not get closest cell id');
    }
}
// middle Mouse click handler
function middleMouseClick()
{
    $('#hackstatus').html('setting target to all CELL IDs');
    // make sure to update the player list when doing this
    playerlist = [];
    command = "/playerlist";
    sendHack(command);
    setTimeout(function() {
        var playerIDs = [];
        for (var key in playerlist) {
            // Skip adding OURSELVES to the middle mouse click list
            if(playerlist[key].id == $('#yourplayerid').html()) {
                continue;
            }
            playerIDs.push(playerlist[key].id);
        }
        if (playerIDs.length) {
            $('#targetplayerid').html(JSON.stringify(playerIDs));
        } else {
            $('#hackstatus').html('Error updating player IDs');
        }
    }, 600);
}

// Add the event listener for key press events
$("body").keydown(keydown);
//window.addEventListener('keyup', keyup);
$("#overlays2").on('mousedown', function(event) {
    //console.log("mouse click event on overlays2 " + event.which);
    //console.log(event);
    if( event.which == 1 ) {
        //event.preventDefault();
        leftMouseClick();
    }
    if( event.which == 2 ) {
        event.preventDefault();
        //middleMouseClick();
    }
});

// global vars to keep stuff in for reference
playerlist = [];
commandlist = [];
playerdetails = [];

// handle server responses to our queries
onMultiChat = function(user, message) {
    if(user == 'SERVER' && message[0] == '/') {
        // remove the leading / and split command at the ": " response
        var split = message.slice(1, message.length).split(': ');
        var command = split[0];
        // remove the command we saved and recombine the array for parsing
        split.splice(0,1);
        var response = split.join().trim();
        // we got an OK response from a command
        if(command == 'ok') { return; }
        // We got our ID back from the server
        if(command == 'playerid') {
            $('#yourplayerid').html(response);
            return;
        }
        // List of supported commands
        if(command == 'commands') {
            commandlist = JSON.parse(response);
            console.log(commandlist);
            return;
        }
        // We got a list of all players from the server
        if(command == 'playerlist') {
            playerlist = JSON.parse(response);
            console.table(playerlist);
            return;
        }
        // We got the servers current configuration
        if(command == 'config') {
            config = JSON.parse(response);
            console.log(config);
            return;
        }
        // We got playerDetails for a client
        if(command == 'playerdetails') {
            playerdetails = JSON.parse(response);
            console.log(playerdetails);
            return;
        }
        console.log('UNHANDLED COMMAND: ' + command);
        console.log(response);
    }
};
