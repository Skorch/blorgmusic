# coding=UTF-8
__author__ = 'abeaupre'

import datetime
import time
import logging
import re, string
from BlorgMusicData.models import  *

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

#take the artist name, convert to all lower-case and strip out any punctuation
def toLowerAndStripPunct(artistName):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    artistName.lower()
    return regex.sub('', artistName.lower())

def to_dict(model):
    output = {}

    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            ms = time.mktime(value.utctimetuple()) * 1000
            ms += getattr(value, 'microseconds', 0) / 1000
            output[key] = int(ms)
        elif isinstance(value, db.GeoPt):
            output[key] = {'lat': value.lat, 'lon': value.lon}
        elif isinstance(value, db.Model):
            output[key] = to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))

    return output

def ParseSongData(InputString, SourceUrl, SourceName, FileUrl, PutData=None):

    htmlOutput = ''
    #tokenize the songData into two pieces seperated by a delimeter
    #one will be the artist and the other will be the track title
    #but we cannot know which is which.

    #break each token futher looking for data contained in ()
    #    eg:  (remix by So and So)
    #        (artist cover)
    #        (ft Another Artist)

    #to detemrin which is which:
    #    1) Check the canonical artist datastore for either tokens
    #    2) optional - look up on Freebase
    #    3) queue data for moderation
#    logging.info('parsing data: %(input)s|%(sourceurl)s|%(sourcename)s|%(fileurl)s' % {'input':InputString, 'sourceurl':SourceUrl, 'sourcename':SourceName, 'fileurl':FileUrl})

    song = ParseItem.get_by_key_name(InputString)
    if song == None:
        logging.info('existing parse item not found')
        coverRegexPattern = re.compile('[(](?P<cover>.+?)(?P<label>cover|cvr)[)]',re.IGNORECASE)
        remixRegexPattern = re.compile('[(](?P<remix>.+?)(?P<label>rmx|mix|remix)[)]',re.IGNORECASE)
        mashupRegexPattern = re.compile('( vs | x )')
        featRegexPattern1 = re.compile('[(](?P<label>ft\s|feat\s|feat\.|ft\.|featuring\s)(?P<feat>.+?)[)]',re.IGNORECASE)
        featRegexPattern2 = re.compile('(?:[(])?(?P<label>ft\s|feat\s|feat\.|ft\.|featuring\s)(?P<feat>.+)(?:[)])?',re.IGNORECASE)
        primaryRegexSplit = re.compile('&#8211;|&#8212;|-|::|[â]|-', re.UNICODE)
        notesRegexPattern= re.compile('[(](?P<notes>.+?)[)]')
        secondaryRegexPattern= re.compile('(?P<second>\(.+?\))')
        logging.info('input string: %s' % InputString )
        song = ParseItem( key_name=InputString, InputString = InputString )
        song.Url = FileUrl
        song.SourceUrl = SourceUrl
        song.Source = SourceName

        #todo:  if primaryRegexSplit results in anythig but two results, raise error
        primarySplitList =re.split(primaryRegexSplit, song.InputString)
#        logging.info('items in primary split %d' % len(primarySplitList))
        if len(primarySplitList) == 2:
            for primaryItem in primarySplitList:
#                logging.info('primaryItem: %s' %primaryItem)
                secondaryResult = re.split(secondaryRegexPattern, primaryItem)
                for secondaryItem in secondaryResult:
                    secondaryMatch = False

                    #search for the existance of a cover song reference
                    matchCover = coverRegexPattern.search(secondaryItem)
                    matchRemix = remixRegexPattern.search(secondaryItem)
                    matchMashup = mashupRegexPattern.search(secondaryItem)
                    matchFeat1 = featRegexPattern1.search(secondaryItem)
                    matchFeat2 = featRegexPattern2.search(secondaryItem)
                    matchNotes = notesRegexPattern.search(secondaryItem)
                    if matchCover:
                        #set result object
                        song.OriginalArtist = StripData(matchCover.group('cover'))
                        secondaryMatch = True
     #                   break
                    elif matchRemix:
                        #set result object
                        song.RemixArtist = StripData(matchRemix.group('remix'))
                        secondaryMatch = True
     #                   break
                    elif matchMashup:
                        #set result object
                        song.IsMashup = True
                        #store the mashup information in the notes field
                        song.SongNotes = StripData(matchNotes.group('notes'))
                        secondaryMatch = True
     #                   break
                    elif matchFeat1:
                        #set result object
                        song.FeaturingArtist = StripData(matchFeat1.group('feat'))
                        secondaryMatch = True
                    elif matchFeat2:
                        song.FeaturingArtist = StripData(matchFeat2.group('feat'))
                        secondaryMatch = False
                        primaryItem = primaryItem.replace(matchFeat2.group('feat'),'')
                        primaryItem = xstr(primaryItem.replace(matchFeat2.group('label'),''))
    #                    break
                        logging.info('secondary item %s'%secondaryItem)
                        song.SongNotes = StripData(matchNotes.group('notes'))
                        secondaryMatch = True

                    if secondaryMatch:
                        primaryItem = primaryItem.replace(secondaryItem,'')

                if song.SongArtist == None:
                    song.SongArtist = StripData(primaryItem)
                elif song.SongTitle == None:
                    song.SongTitle = StripData(primaryItem)
            if(PutData):
                song.put()
        else:
            logging.info('found an existing parse item.')
    return song

def formatSongTitle( songPost ):
    if songPost.CanonicalSong is None:
        return 'error'
    songArtist = songPost.CanonicalSong.SongArtist.Name
    songTitle = songPost.CanonicalSong.SongTitle

    featArtist = ''
    if songPost.CanonicalSong.FeaturingArtist != None:
        featArtist = ' (ft. %s)' % songPost.CanonicalSong.FeaturingArtist.Name

    remixArtist = ''
    if songPost.CanonicalSong.RemixArtist != None:
        remixArtist = ' (%s Remix)' % songPost.CanonicalSong.RemixArtist.Name

    coverArtist = ''
    if songPost.CanonicalSong.OriginalArtist != None:
        coverArtist = ' (%s Cover)' % songPost.CanonicalSong.OriginalArtist.Name

    isMashupText = ''
    if songPost.CanonicalSong.IsMashup:
        isMashupText = ' (Mashup)'

    #todo:  compile a javascript array of the data to store this information to display dynamically
    sourceName = 'unknown source'
    if songPost.Blog != None:
        if songPost.Blog.Blog != None:
            sourceName = songPost.Blog.Blog.BlogUrl

    return '%(songartist)s%(feat)s - %(songtitle)s%(cover)s%(remix)s%(mash)s <br> %(sourcename)s' %{
         'songartist': songArtist,
         'feat': featArtist,
         'songtitle': songTitle,
         'cover': coverArtist,
         'mash': isMashupText,
         'remix': remixArtist,
         'sourcename': sourceName
         }



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

