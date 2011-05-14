import logging
import os
from BlorgMusicData.models import DataSource, SongPost
from BlorgMusicHelper.stringhelper import *
from google.appengine.ext import db

__author__ = 'abeaupre'

#app_id = 'XXXXXX'
#os.environ['APPLICATION_ID'] = app_id

def fetchSourceList():
    return DataSource.all()

def fetchSongPostList(sourceKey = None, page = 1, size = 50):
    comma = ''
    songOutput = ''
    pageOffset = (page-1)*size
    songList = []
    dataSourceItem = None
    if sourceKey:
        dataSourceItem = DataSource.get(sourceKey)
    else:
        dataSource = None
    dataLength = 0
    #logging.info("fetchSongPostList: sourceKey=%s" % sourceKey)
    if dataSourceItem:
        #1) get data source
        #2) get filtered list of songPosts in the SongPostDataSourceList bridge table
        #3) get actual SongPost and append it to the list
        songPostDataSourceList = dataSourceItem.SongPostList.order('-CreateTime').fetch(size, pageOffset)
        for songPostDataSourceItem in songPostDataSourceList:
            songList.append(songPostDataSourceItem.SongPost)
        dataLength = dataSourceItem.SongPostList.count()
    else:
        #logging.info("fetching size %(size)s with offset %(offset)s" % {'size':size, 'offset':pageOffset})
        songPostQuery = SongPost.all().order("-CreateTime").fetch(size, pageOffset)
        #logging.info("song list with length of %s" % len(songPostQuery))
        songList.extend(songPostQuery)
        dataLength = SongPost.all().count()

    result = dict()
    result['songList'] = songList
    result['dataLength'] = dataLength
    return result


