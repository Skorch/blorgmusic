import logging
import os
from BlorgMusicData.models import DataSource, SongPost
from BlorgMusicHelper.stringhelper import *
from google.appengine.ext import db

__author__ = 'abeaupre'



class Dao():
    @classmethod
    def fetchSourceList(cls):
        return DataSource.objects.all()

    @classmethod
    def fetchSongPostList(cls, sourceKey = None, page = 1, size = 50):
        dataSource = None
        if sourceKey:
            dataSource = DataSource.objects.get(pk=sourceKey)

        songList = Dao.GetSongPostList(dataSource, size, page, 'CreateTime', True)

        if dataSource:
            dataLength = SongPostDataSourceList.objects.filter(DataSource_id = dataSource.id).count()
        else:
            dataLength = SongPost.objects.count()

        result = dict()
        result['songList'] = songList
        result['dataLength'] = dataLength
        return result

    @classmethod
    def ArtistItem_GetOrAdd(cls, name, hasCover=False, hasFeaturing=False, hasMashup=False, hasRemix=False):
        return ArtistItem.objects.get_or_create(Name=name, defaults=
            {'HasRemix':hasRemix, 'HasMashup':hasMashup, 'HasCover':hasCover, 'HasFeaturing':hasFeaturing})[0]

    @classmethod
    def GetArtistItem(cls, key):
        return ArtistItem.objects.get(key)

    @classmethod
    def GetArtistItemList(cls, pageSize, pageOffset, orderBy, orderDesc):
        itemOffset = (pageOffset-1)*pageSize
        orderString = ('-' if orderDesc else '') + orderBy
        return ArtistItem.objects.order_by(orderString)[itemOffset:pageSize]

    @classmethod
    def SongItem_GetList(cls, pageSize, pageOffset, orderBy, orderDesc):
        itemOffset = (pageOffset-1)*pageSize
        orderString = ('-' if orderDesc else '') + orderBy
        itemList = SongItem.objects.order_by(orderString)[itemOffset:pageSize]
        for item in itemList:
            item.ArtistRoleList = Dao.SongArtistRoleList_GetAll(item)

    @classmethod
    def GetParseItemList(cls, pageSize, pageOffset, orderBy, orderDesc):
        itemOffset = (pageOffset-1)*pageSize
        orderString = ('-' if orderDesc else '') + orderBy
        return ParseItem.objects.order_by(orderString)[itemOffset:pageSize]

    @classmethod
    def SongItem_Get(cls, key):
        songItem = SongItem.objects.get(pk=key)
        songItem.ArtistRoleList = Dao.SongArtistRoleList_GetAll(songItem)
        return songItem

    @classmethod
    def GetParseItem(cls, key):
        return ParseItem.objects.get(pk=key)

    @classmethod
    def GetSongPost(cls, key):
        return SongPost.objects.get(pk=key)

    @classmethod
    def GetBlogPost(cls, key):
        return BlogPost.objects.get(pk=key)

    @classmethod
    def GetSongPostList(cls, dataSource, pageSize, pageOffset, orderBy, orderDesc):
        itemOffset = (pageOffset-1)*pageSize
        orderString = ('-' if orderDesc else '') + orderBy
        if dataSource:
            #return SongPostDataSourceList.objects.filter(DataSource_id = dataSourceId).order_by(orderString)[itemOffset:pageSize]
            #TODO:  determine the best way to perform this query.  Denormalization or get list of SongPostIDs and iterate or investigate django-nonrel Indexing module (supports joins)
            songPostSourceList = SongPostDataSourceList.objects.filter(DataSource_id = dataSource.id).order_by(orderString)[itemOffset:pageSize]
            songPostList = []
            for item in songPostSourceList:
                songPost = SongPost.objects.get(pk=item.SongPost_id)
                songPostList.append(songPost)
            return songPostList
        else:
            return SongPost.objects.order_by(orderString)[itemOffset:pageSize]

    @classmethod
    def SongPost_AddFromParseData(cls, parsedText, songUrl, blogPostItem):
        if parsedText['successful']:

            songTitle = parsedText['songTitle']
            primaryArtistName = parsedText['primaryArtist']
            artistRoleList = parsedText['artistRoleList']
            songNotes = parsedText['songNote']
            inputString = parsedText['inputString']


            #for each of the listed artists, getoradd
            songKeyArtists = []
            primaryArtist = None
            for artistRole in artistRoleList:
                roleType = artistRole['role']
                artistName = artistRole['name']
                artistItem = cls.ArtistItem_GetOrAdd(artistName)
                if artistItem:
                    songKeyArtists.append({'artistItem':artistItem, 'roleType': roleType})
                    if roleType == 'P':
                        primaryArtist = artistItem




            #generate the SongKey
            songKey = cls.generateSongKey(songTitle, songKeyArtists)
            formattedSongTitle = formatSongTitle(songTitle, songNotes, artistRoleList)

            #look for the existing song
            songItemDefaults = {
                'SongTitle':songTitle,
                'FormattedSongTitle':formattedSongTitle,
                'SongNotes':songNotes,
                'PrimaryArtist': primaryArtist
            }


            songItem =  SongItem.objects.get_or_create(SongKey=songKey, defaults=songItemDefaults)[0]
            songPostDefaults = {
                'CanonicalSong' : songItem,
                'Blog' : blogPostItem,
                'OriginalText': inputString
            }
            return SongPost.objects.get_or_create(SongUrl = songUrl, defaults=songPostDefaults)[0]

    @classmethod
    def AddParseItem(cls, parsedText):
        inputString = parsedText['inputString']
        return ParseItem.objects.get_or_create(InputString=inputString)[0]
    
    @classmethod
    def AddParseItemSourceItemList(cls, parsedSong, dataSource):
        logging.info(parsedSong)
        return ParseItemSourceList.objects.get_or_create(Parse = parsedSong, SourceItem = dataSource)[0]

    @classmethod
    def GetDataSource(cls, dataSourceName):
        try:
            dataSource = DataSource.objects.get(SourceName=dataSourceName)
        except DataSource.DoesNotExist:
            dataSource = None
        return dataSource

    @classmethod
    def GetOrAddParseItem(cls, inputString, mp3href, blogPostItem):
        try:
            parseItem = ParseItem.objects.get(InputString=inputString)
        except ParseItem.DoesNotExist:
            parseItem = ParseItem(InputString=inputString, Url=mp3href, SourceUrl=blogPostItem.PostUrl)
            parseItem.save()
        return parseItem

    @classmethod
    def BlogSource_GetOrInsert(cls, sourceDomain, blogName):
        return BlogSource.objects.get_or_create(BlogUrl=sourceDomain, defaults={'BlogName':blogName})[0]

    @classmethod
    def BlogPost_GetOrInsert(cls, sourceUrl, blogPostSummary, blogSource):
        return BlogPost.objects.get_or_create(PostUrl = sourceUrl, defaults={'Summary':blogPostSummary, 'Blog':blogSource})[0]

    @classmethod
    def BlogPost_Get(cls, sourceUrl):
        return BlogPost.objects.get(PostUrl = sourceUrl)

    
    @classmethod
    def DeleteArtistItem(cls, artistItem):
        artistItem.delete()

    @classmethod
    def DeleteSongItem(cls, songItem):
        songItem.delete()

    @classmethod
    def DeleteParseItem(cls, parseItem):
        parseItem.delete()

    @classmethod
    def DataSource_GetOrAdd(cls, dataSourceName, dataSourceUrl):
        return DataSource.objects.get_or_create(SourceName = dataSourceName, defaults={'SourceUrl': dataSourceUrl})[0]

    @classmethod
    def FormatSongKey(cls, songTitle):
        return toLowerAndStripPunct(songTitle)


    # Key is defined as:
    #  formatted title + a sorted list of artistIds in CSV
    @classmethod
    def generateSongKey(cls, songTitle, artistRoleList):
        artistKey =''
        comma = ''
        for artistRoleItem in sorted(artistRoleList, key=lambda roleItem: roleItem['artistItem'].id):
            if artistRoleItem['roleType'] in['P', 'R', 'M']:
                artistKey += comma + str(artistRoleItem['artistItem'].id)
                comma =','
        return cls.FormatSongKey(songTitle) + '_' + artistKey

    @classmethod
    def DataSource_GetListAll(cls):
        dataSourceList = DataSource.objects.all()
        if not dataSourceList:
            Dao.DataSource_GetOrAdd('twitter', 'http://api.twitter.com/1/evilnohear/lists/all-music/statuses.xml')
            Dao.DataSource_GetOrAdd('twitter-electronic', 'http://api.twitter.com/1/evilnohear/lists/electronic-blogs/statuses.xml')
            Dao.DataSource_GetOrAdd('twitter-indie', 'http://api.twitter.com/1/evilnohear/lists/indie-blogs/statuses.xml')

        return dataSourceList

    @classmethod
    def ParseItem_GetListAll(cls):
        return ParseItem.objects.all()

    @classmethod
    def SongArtistRoleList_GetAll(cls, songItem):
        SongArtistRoleList.objects.filter(Song=songItem)


