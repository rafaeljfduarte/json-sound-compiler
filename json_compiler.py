#!/usr/bin/env python

import json
import os
import sys

ROOT_PATH = "/opt/lampp/htdocs"

Positions = {}
MIX = []
BASE = ""
LAST = ""
SOUNDS = ROOT_PATH + "/site-assets/sounds"
FOLDER = ROOT_PATH + "/uploads/" + sys.argv[1]

# Direct path to the FFMPEG execution path.
FFMPEG = "ffmpeg"

print ("++ USER FOLDER: " + str(sys.argv[1]) + " ++")

## Creating the positions array
with open(FOLDER + '/mix.json') as json_file:
    data = json.load(json_file)
    #print(data['participation'])
    for m in data['mix']:
        print('Track: ' + m['track'])
        print('Position: ' + str(m['position']))
        print('Volume: ' + str(m['volume']))
        if (m['position'] in Positions):
            Positions[m['position']].append(str(m['volume'])+'/'+m['track'])
        else:
            Positions[m['position']] = [str(m['volume'])+'/'+m['track']]
    BASE = SOUNDS + '/50/' + str(data['base']) # hardcoded path & volume
    print('Base: ' + BASE)

## == MIX COLUMN SOUNDS WHERE TWO SOUNDS OR MORE ARE IN THE SAME COLUMN
print(Positions)
print ("++ SEQUENCE ++")
for i in range(0,10):
    FFMPEG_MIX = FFMPEG + " -y "
    try:
        print ("--")
        print("POSITION: " + str(i))
        print("TRACKS: ")
        print(Positions[i])
        if len(Positions[i]) > 1:
            print("++ IM HERE ++")
            for j in Positions[i]:
                FFMPEG_MIX += " -i " + SOUNDS + "/" + str(j)
            FFMPEG_MIX += ' -filter_complex "[0:0][1:0] amix=inputs=' + str(len(Positions[i])) + ':duration=longest" ' + FOLDER  + '/mix' + str(i) + '.mp3'
            MIX.append(i)
            print
            print("-- EXECUTING MIX " + str(i) + " : " + FFMPEG_MIX)
            print
            os.system(FFMPEG_MIX)
    except KeyError:
        print ("-- Silence")
        FFMPEG = FFMPEG + " -y "

# == SHOW ME THE COLUMNS THAT WERE MIXED

print ("++ MIXES ++")
print(MIX)

## CREATE THE FFMPEG SCRIPT TO MERGE ALL SOUNDS WITH BASE
FFMPEG = FFMPEG + ' -y -i ' + SOUNDS + '/silence.mp3'

FFMPEG_FILTER = ' -filter_complex "[0]adelay=0|0,volume=10[0:a];'
FFMPEG_END = '[0:a]'

INPUTS = 1

for i in range(1,10):
    try:
        if len(Positions[i]) == 1:
            FFMPEG += " -i " + SOUNDS + "/" + Positions[i][0]
            FFMPEG_FILTER += '['+ str(INPUTS) +']adelay=' + str(i) + '000|' + str(i) + '000,volume=5['+ str(INPUTS) +':a];'
            FFMPEG_END += '['+ str(INPUTS ) +':a]'
            INPUTS += 1
			if len(AttrObject) > 2:
				INPUTS = 0
        if len(Positions[i]) > 1:
            FFMPEG += " -i " + FOLDER + "/mix" + str(i) + ".mp3"
            FFMPEG_FILTER += '['+ str(INPUTS) +']adelay=' + str(i) + '000|' + str(i) + '000,volume=5['+ str(INPUTS) +':a];'
            FFMPEG_END += '['+ str(INPUTS) +':a]'
            INPUTS += 1
    except KeyError:
        print ("-- Silence")
        pass

FFMPEG += ' -i ' + BASE
FFMPEG_FILTER += '['+ str(INPUTS) +']adelay=0|0,volume=1['+ str(INPUTS) +':a];'
FFMPEG_END += '[' + str(INPUTS) + ':a]'

#CREATE THE FINAL FFMPEG

EXEC_FFMPEG = FFMPEG + FFMPEG_FILTER + FFMPEG_END + 'amix=inputs=' + str(INPUTS + 1) + ':dropout_transition=0,dynaudnorm" -q:a 1 -acodec libmp3lame -y  ' + FOLDER + '/mix.mp3 2>&1'

os.system(EXEC_FFMPEG)
print(EXEC_FFMPEG)
