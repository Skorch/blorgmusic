import logging
from BlorgMusicHandler.jsonresponse import *
from BlorgMusicData.dao import Dao
from BlorgMusicHelper.stringhelper import str2none
from django.template.loader import render_to_string


class BlorgMusicServices(JsonWebService):

    @JsonWebService.jsonresponse()
    def ArtistSongs(self, request):
        artistKey = request.GET.get('artistkey').strip()
        artistItem = Dao.GetArtistItem(artistKey)

        #TODO:  use python model-JSON serializer
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

    def render_musicstream(self, sourceStr, pageNumber, size):
        songPostListResult = Dao.fetchSongPostList(sourceStr, pageNumber, size)
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
