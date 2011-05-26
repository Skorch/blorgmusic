from BlorgMusicIngestPipeline.parseinput import ParseInput
from django.http import HttpResponse
#sys.path.append('py')
from BeautifulSoup.beautifulsoup import BeautifulSoup
from google.appengine.api import urlfetch
from urlparse import urlparse
from django.views.decorators.csrf import csrf_exempt
from BlorgMusicData.dao import *


def formatSongTitle( songTitle):
    return songTitle.replace('"','')


def parseNodeData( htmlNodeString):

    badTitlePattern = re.compile('^(mp3|download|[>]|None)$')

    soup = BeautifulSoup(htmlNodeString)
    mp3List = soup.findAll('a', href=re.compile('.mp3$'))

    nodeList = []

    for htmlNode in mp3List:

        mp3url = htmlNode['href']

        nodeTitle = getattr(htmlNode, 'title', lambda:None)
        if nodeTitle is None and htmlNode.string:
            if not len(badTitlePattern.findall(htmlNode.string, re.IGNORECASE)):
                nodeTitle = htmlNode.string

        #if there are elements within the anchor, strip them out
        if nodeTitle is None and htmlNode.string is None:
            nodeTitle = ''.join(htmlNode.findAll(text=True))

#                for childNode in htmlNode:
#                    #nodeTitle += childNode.string
#                    logging.info('removing child node %s' % childNode)
#                    childNode.extract()
            #if htmlNode.string == None:

#               nodeTitle = htmlNode.string

            #if after scrubbing the children of the anchor node, try a parent
#              if len(htmlNode) == 0:
#                 parentNode =



        if nodeTitle is not None and nodeTitle != '':
            nodeList.append({'mp3url':mp3url, 'title':nodeTitle})

    return nodeList

@csrf_exempt
def main(request):
    #parseUrlList = ['http://www.indieshuffle.com']#, 'http://www.aquariumdrunkard.com/']

#        defaultSource = MusicSource(key_name='indieshuffle', SourceName='indieshuffle', SourceUrl='http://www.indieshuffle.com')
#       defaultSource.put()

    if request.method == 'GET':

        parseUrl = request.GET.get('dataUrl')
        sourceName = request.GET.get('dataSource')

        fetchSongData(parseUrl, sourceName)

    else:
        errorOutput = 'expected GET method'
        logging.error(errorOutput)


    return HttpResponse('success')

def fetchSongData(parseUrl, sourceName):
    try:

        page = urlfetch.fetch(parseUrl)
        if page.status_code == 200:

            if page.final_url is not None:
                try:
                    sourceUrl = unicode(page.final_url) #page.headers["Location"]  #page.geturl()
                except UnicodeDecodeError:
                    sourceUrl = parseUrl
            else:
                sourceUrl = parseUrl

            nodeList = parseNodeData(page.content)

            blogName = 'TODO:  Get blog name from meta data'
            parsedUrl = urlparse(sourceUrl)
            if parsedUrl is not None:
                sourceDomain = parsedUrl[1]
            else:
                sourceDomain = ""

            #weird re-direct URLs like Stumbleupon cause messed up redirect urls - default
            if sourceDomain == "":
                sourceDomain = "unknown"
                sourceUrl = parseUrl

            blogSource = Dao.BlogSource_GetOrInsert(sourceDomain, blogName)

            blogPostSummary = 'TODO:  Add blog summary'
            blogPostItem = Dao.BlogPost_GetOrInsert(sourceUrl, blogPostSummary, blogSource)


            for mp3Link in nodeList:

                #data that's returned from the ParseNodeData func
                mp3href = mp3Link['mp3url']
                songTitle = mp3Link['title']



                if songTitle is not None:
                    #call helper to parse the text into an object
                    #TODO:  Make 'ArtistFirst' configurable at the Blog level
                    parsedText = ParseInput.ParseSongTitle(formatSongTitle(songTitle), True)

                    #parsing was not successful.  Log for manual review
                    if not parsedText['successful']:

                        parsedSong = Dao.GetOrAddParseItem( songTitle, mp3href, blogPostItem )

                        #check for the parseItem-Source link
                        dataSource = Dao.GetDataSource(sourceName)
                        if not dataSource:
                            dataSource = Dao.GetDataSource('unknown')

                        #store the relationship between the parseItem and the source
                        #TODO:  remove this and add it to the point where the song is created/retreived
                        Dao.AddParseItemSourceItemList(parsedSong, dataSource)

                    else:
                        Dao.SongPost_AddFromParseData(parsedText, mp3href, blogPostItem)

                else:
                    logging.info("Could not parse data - no title found.  url: %s " % parseUrl)
            else:
                logging.info("URL Fetch returned an error. %s" % page.status_code)
    except urlfetch.Error:
        errorMessage = '<li>error fetching URL %s</li>' % parseUrl
        logging.error(errorMessage)
    except UnicodeEncodeError:
        errorMessage = '<li>not an HTML document at url: %s</li>' % parseUrl
        logging.error(errorMessage)




