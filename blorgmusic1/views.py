from BlorgMusicData.dao import Dao
from BlorgMusicHelper.stringhelper import *
from django.shortcuts import render_to_response

def render(request):
    #TODO:  convert this into a fully RESTful syntax
    pageNumberStr = str2none(request.GET.get('p'))
    sizeStr = str2none(request.GET.get('s'))
    sourceStr = str2none(request.GET.get('src'))
#    logging.info('pageNumber: %(p)s, size: %(s)s, source: %(src)s' %{'p':pageNumberStr, 's': sizeStr, 'src':sourceStr})
    if pageNumberStr:
        pageNumber = int(pageNumberStr)
    else:
        pageNumber = 1
    if sizeStr:
        size = int(sizeStr)
    else:
        size = 50
    songPostListResult =  Dao.fetchSongPostList(sourceStr, pageNumber, size)
    payload = dict()
    #payload['javascriptSongList'] = javascriptBuilder.buildSongPlaylist(songPostList)
    payload['songlist'] = songPostListResult['songList']
    payload['datalength'] = songPostListResult['dataLength']
    payload['moredata'] = (songPostListResult['dataLength'] > pageNumber *size)
    payload['currentpage'] = pageNumber
    payload['pagesize'] = size
    payload['sourcekey'] = sourceStr
    payload['sourcelist'] = Dao.fetchSourceList()
    return render_to_response('index.html', payload)


