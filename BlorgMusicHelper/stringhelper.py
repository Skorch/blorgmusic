# coding=UTF-8

__author__ = 'abeaupre'

import datetime
import time
import logging
import re, string
from BlorgMusicData.models import  *


#take the artist name, convert to all lower-case and strip out any punctuation
def toLowerAndStripPunct(artistName):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    artistName.lower()
    return regex.sub('', artistName.lower())


def formatSongTitle( songTitle, songNote, artistRoleList ):

    primaryArtistList = []
    remixArtistList = []
    mashupArtistList = []
    featuringArtistList = []
    originalArtistList = []

    primaryString = ''
    remixString = ''
    mashupString = ''
    featuringString = ''
    originalString = ''

    for artistRole in artistRoleList:
        if artistRole['role'] == 'P':
            primaryArtistList.append(artistRole['name'])
        if artistRole['role'] == 'R':
            remixArtistList.append(artistRole['name'])
        if artistRole['role'] == 'M':
            mashupArtistList.append(artistRole['name'])
        if artistRole['role'] == 'F':
            featuringArtistList.append(artistRole['name'])
        if artistRole['role'] == 'O':
            originalArtistList.append(artistRole['name'])

    if len(remixArtistList):
        remixString = ' (%s Remix)' % ','.join(remixArtistList)

    if len(mashupArtistList):
        mashupString = ' (%s)' % ' vs '.join(mashupArtistList)

    if len(featuringArtistList):
        featuringString = ' (ft. %s)' % ','.join(featuringArtistList)

    if len(originalArtistList):
        originalString = ' (%s cover)' % ','.join(originalArtistList)

    if len(primaryArtistList):
        primaryString = '%s' % ' and '.join(primaryArtistList)

    return primaryString + featuringString + ' - ' + songTitle + remixString + mashupString + originalString + songNote


def StripData(InputString):
    if InputString:
        return InputString.strip()
    else:
        return None
    
def str2none(st):
    if st == '':
        return None
    elif st == 'None':
        return None
    return st
def str2bool(st):
    if st == 'True':
        return True
    else:
        return False

def xstr(st):
    newstr = st
    if st is None:
        return ''
    logging.info(st)
    reStrip = re.compile('\"|\“|\”|&#8220;|&#8221;')
    newstr = reStrip.sub('', st)
    return newstr

