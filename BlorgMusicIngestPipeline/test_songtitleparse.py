import logging
from BlorgMusicHelper.stringhelper import ParseSongData
from django.http import HttpResponse
from django.shortcuts import render_to_response


def main(request):
    InputString = request.GET.get('input')
    SourceUrl = ''
    SourceName = ''
    FileUrl = ''
    logging.info("input: %s" % InputString)
    songItem = ParseSongData(InputString, SourceUrl, SourceName, FileUrl)

    htmlOutput = """
    <html>
        <head><title>test</title></head>
        <body>
    """

    htmlOutput += "<li>InputString: %s</li>" % songItem.InputString
    htmlOutput += "<li>SongTitle: %s</li>" % songItem.SongTitle
    htmlOutput += "<li>SongArtist: %s</li>" % songItem.SongArtist
    htmlOutput += "<li>RemixArtist: %s</li>" % songItem.RemixArtist
    htmlOutput += "<li>IsMashup: %s</li>" % songItem.IsMashup
    htmlOutput += "<li>FeatArtist: %s</li>" % songItem.FeaturingArtist
    htmlOutput += "<li>OriginalArtist: %s</li>" % songItem.OriginalArtist
    htmlOutput += "<li>SongNotes: %s</li>" % songItem.SongNotes

    htmlOutput += """
        </body>
    </html>
    """

    return HttpResponse(htmlOutput)

    

