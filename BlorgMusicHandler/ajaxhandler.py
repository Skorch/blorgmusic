import logging
from BlorgMusicData.dao import fetchSongPostList
from BlorgMusicHelper.stringhelper import *
from BlorgMusicHandler.jsonresponse import *
from BlorgMusicData.models import *
from BlorgMusicData.dao import *
from django.template.loader import render_to_string



class BlorgMusicServices(JsonWebService):

    @JsonWebService.jsonresponse()
    def ArtistSongs(self, request):
        artistKey = request.GET.get('artistkey').strip()
        artistItem = ArtistItem.get(artistKey)
        if artistItem:
            return self.db2dict(artistItem.PrimarySongs.fetch(3))
        else:
            return None

    @JsonWebService.jsonresponse()
    def SongStream(self, request):
        #TODO:  convert this into a fully RESTful syntax
        pageNumberStr = str2none(request.GET.get('p'))
        sizeStr = str2none(request.GET.get('s'))
        sourceStr = str2none(request.GET.get('src'))
        logging.info('pageNumber: %(p)s, size: %(s)s, source: %(src)s' %{'p':pageNumberStr, 's': sizeStr, 'src':sourceStr})
        if pageNumberStr:
            pageNumber = int(pageNumberStr)
        else:
            pageNumber = 1
        if sizeStr:
            size = int(sizeStr)
        else:
            size = 50

        return self.render_musicstream(sourceStr, pageNumber, size)

    def db2dict(self, result):
        if isinstance(result, list):
            resultList = []
            for resultItem in result:
                resultList.append( to_dict(resultItem) )
            return resultList
        else:
            return result

    def render_musicstream(self, sourceStr, pageNumber, size):
        songPostListResult = fetchSongPostList(sourceStr, pageNumber, size)
        payload = dict()
        #payload['javascriptSongList'] = javascriptBuilder.buildSongPlaylist(songPostList)
        payload['songlist'] = songPostListResult['songList']
        payload['datalength'] = songPostListResult['dataLength']
        payload['moredata'] = (songPostListResult['dataLength'] > pageNumber*size)
        payload['currentpage'] = pageNumber
        payload['pagesize'] = size
        payload['source'] = sourceStr

        return render_to_string('songstream.html', payload)


ws = BlorgMusicServices()
