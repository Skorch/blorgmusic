# coding=UTF-8

import re
from BlorgMusicHelper.stringhelper import StripData, xstr

__author__ = 'abeaupre'

ROLE_PRIMARY = "P"
ROLE_REMIX = "R"
ROLE_FEATURING = "F"
ROLE_ORIGINAL = "O"
ROLE_MASHUP = "M"


class ParseInput:

    @classmethod
    def ParseSongTitle(cls, inputString, artistFirst):

        #Regex to figure out which piece is which
        coverRegexPattern = re.compile('[(](?P<value>.+?)(?P<label>cover|cvr)[)]',re.IGNORECASE)
        remixRegexPattern = re.compile('[(](?P<value>.+?)(?P<label>rmx|mix|remix)[)]',re.IGNORECASE)
        mashupRegexPattern = re.compile('( vs | x )')
        featRegexPattern1 = re.compile('[(](?P<label>ft\s|feat\s|feat\.|ft\.|featuring\s)(?P<value>.+?)[)]',re.IGNORECASE)
        featRegexPattern2 = re.compile('(?:[(])?(?P<label>ft\s|feat\s|feat\.|ft\.|featuring\s)(?P<value>.+)(?:[)])?',re.IGNORECASE)
        primaryRegexSplit = re.compile('&#8211;|&#8212;|-|::|[â]|-', re.UNICODE)
        notesRegexPattern= re.compile('[(](?P<value>.+?)[)]')
        secondaryRegexPattern= re.compile('(?P<second>\(.+?\))')

        primarySplitList =re.split(primaryRegexSplit, inputString)

        #list to hold artist roles
        artistRoleList = []
        comma = ''
        isFirst = True
        parseSuccessful = False
        songTitle = ''
        songNotes = ''
        primaryArtist = ''

        if len(primarySplitList) == 2:
            for primaryItem in primarySplitList:
#                logging.info('primaryItem: %s' %primaryItem)
                secondaryResult = re.split(secondaryRegexPattern, primaryItem)
                for secondaryItem in secondaryResult:
                    secondaryMatch = False

                    #search for the existence of a cover song reference
                    regexList1 = [{'regex': mashupRegexPattern, 'type': 1, 'role': ROLE_MASHUP},
                                  ({'regex': coverRegexPattern, 'type': 1, 'role': ROLE_ORIGINAL}),
                                  ({'regex': remixRegexPattern, 'type': 1, 'role': ROLE_REMIX}),
                                  ({'regex': featRegexPattern1, 'type': 1, 'role': ROLE_FEATURING}),
                                  ({'regex': featRegexPattern2, 'type': 2, 'role': ROLE_FEATURING}),
                                  {'regex': notesRegexPattern, 'type': 0, 'role': None}]
                    for regexItem in regexList1:

                        matchResult = regexItem['regex'].search(secondaryItem)
                        artistRole = regexItem['role']
                        matchType = regexItem['type']
                        if matchResult:
                            matchString = StripData(matchResult.group('value'))
                            matchLabel = StripData(matchResult.group('label'))
                            if matchType == 1:
                                artistRoleList.append({'name':matchString, 'label':matchLabel, 'role':artistRole})
                                secondaryMatch = True
                            #a specific case for Featuring artists w/o ()
                            #TODO:  can this be rolled into Type 1?
                            elif matchType == 2:
                                artistRoleList.append({'name':matchString, 'label':matchLabel, 'role':artistRole})
                                primaryItem = primaryItem.replace(matchString,'')
                                primaryItem = xstr(primaryItem.replace(matchLabel,''))
                                secondaryMatch = False
                            else:
                                songNotes += comma + matchString
                            break

                    if secondaryMatch:
                        primaryItem = primaryItem.replace(secondaryItem,'')

                if isFirst:
                    if artistFirst:
                        primaryArtist = StripData(primaryItem)
                        artistRoleList.append({'name':primaryArtist, 'role':ROLE_PRIMARY})
                    else:
                        songTitle = StripData(primaryItem) if artistFirst else StripData(songTitle)
                    isFirst = False
                else:
                    if not artistFirst:
                        primaryArtist = StripData(primaryItem)
                        artistRoleList.append({'name':primaryArtist, 'role':ROLE_PRIMARY})
                    else:
                        songTitle = StripData(primaryItem) if artistFirst else StripData(songTitle)

        #minimum requirements for a successful parse:  song title and primary artist
        if songTitle and primaryArtist > 0:
            parseSuccessful = True
        return {'successful': parseSuccessful, 'primaryArtist': primaryArtist, 'songTitle': songTitle, 'songNote': songNotes, 'artistRoleList':artistRoleList, 'inputString': inputString}