
from django.http import HttpResponse, HttpResponseRedirect
#sys.path.append('py')
from BeautifulSoup.beautifulsoup import BeautifulSoup
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext import db
import re
import logging
from urlparse import urlparse
from BlorgMusicData.models import  *
from BlorgMusicHelper.stringhelper import  *
from django.views.decorators.csrf import csrf_exempt



def formatSongTitle( songTitle):
    return songTitle.replace('"','')


def parseNodeData( htmlNodeString):

    badTitlePattern = re.compile('^(mp3|download|[>]|None)$')

    soup = BeautifulSoup(htmlNodeString)
    mp3List = soup.findAll('a', href=re.compile('.mp3$'))

    nodeList = []

    for htmlNode in mp3List:
        nodeTitle = None
        mp3url = htmlNode['href']

        nodeTitle = getattr(htmlNode, 'title', lambda:None)
        if nodeTitle == None and htmlNode.string:
            if len(badTitlePattern.findall(htmlNode.string, re.IGNORECASE)) == 0:
                nodeTitle = htmlNode.string

        #if there are elements within the anchor, strip them out
        if nodeTitle==None and htmlNode.string == None:
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



        if nodeTitle != None and nodeTitle != '':
            nodeList.append({'mp3url':mp3url, 'title':nodeTitle})
        logging.info('====attribute text: %(node)s | title:"%(title)s"' % {'node':htmlNode.string, 'title':nodeTitle})

    return nodeList

@csrf_exempt
def main(request):
    logging.info('=====fetching data')
    #parseUrlList = ['http://www.indieshuffle.com']#, 'http://www.aquariumdrunkard.com/']

#        defaultSource = MusicSource(key_name='indieshuffle', SourceName='indieshuffle', SourceUrl='http://www.indieshuffle.com')
#       defaultSource.put()
    parseUrl = ''
    sourceName = ''
    hrefList = []
#    logging.info( 'request object: %s' % request)
    if request.method == 'GET':

        parseUrl = request.GET.get('dataUrl')
        sourceName = request.GET.get('dataSource')

        errorOutput = ''

        hrefList = []

        try:

            page = urlfetch.fetch(parseUrl)
            if page.status_code == 200:

                if page.final_url != None:
                    try:
                        sourceUrl = unicode(page.final_url) #page.headers["Location"]  #page.geturl()
                    except UnicodeDecodeError:
                        sourceUrl = parseUrl
                else:
                    sourceUrl = parseUrl
                logging.info("final url: %s" % page.final_url)
                #logging.info( ''.join(page.headers.keys()))
                nodeList = parseNodeData(page.content)

                blogName = 'TODO:  Get blog name from meta data'
                parsedUrl = urlparse(sourceUrl)
                if parsedUrl != None:
                    sourceDomain = parsedUrl[1]
                    logging.info("source Domain: %s" % sourceDomain)
                    logging.info("source url: %s" % sourceUrl)
                else:
                    sourceDomain = ""
                #weird re-direct URLs like Stumbleupon cause messed up redirect urls - default
                if sourceDomain == "":
                    sourceDomain = "unknown"
                    sourceUrl = parseUrl

                blogSource = BlogSource.get_or_insert(key_name=sourceDomain, BlogUrl=sourceDomain, BlogName=blogName)
                blogSource.put()
                blogPostSummary = 'TODO:  Add blog summary'
                blogPostItem = BlogPost.get_or_insert(key_name=sourceUrl, PostUrl = sourceUrl)

                blogPostItem.Summary = blogPostSummary
                blogPostItem.Blog = blogSource
                blogPostItem.put()

                #soup = BeautifulSoup(page.content)
                #mp3List = soup.findAll('a', href=re.compile('.mp3$'))
                if len(nodeList) == 0:
                    logging.info('no mp3s found on page %s' % parseUrl)

                for mp3Link in nodeList:

                    #data that's returned from the ParseNodeData func
                    mp3href = mp3Link['mp3url']
                    songTitle = mp3Link['title']

                    if songTitle != None and songTitle != '':


                        logging.info('fetching url: %s' % mp3href)
                        #mp3Data = SongPost.get_by_key_name(mp3href)
                        mp3Data = None
                        #logging.info('mp3 info: %(content)s, %(url)s' %{'content':songTitle, 'url': mp3href})
                        if mp3Data == None:
                            logging.info(u'mp3 not in datastore.  creating new object: %(content)s, %(url)s' %{'content':formatSongTitle(songTitle), 'url': mp3href})
        #                    mp3Data = MusicItem(key_name = mp3href, Url = mp3href, Source = sourceName, SourceUrl = sourceUrl, SongTitle = formatSongTitle(songTitle) )

                            parsedSong = ParseSongData(formatSongTitle(songTitle), sourceUrl, sourceName, mp3href, True)

                            #check for the parseItem-Source link

                            sourceItemList = DataSource.gql("WHERE SourceName=:1", sourceName ).fetch(1)
                            if sourceItemList == None:
                                sourceItemList = DataSource.gql("WHERE SourceName=:1", "unknown" ).fetch(1)
                            if sourceItemList == None:
                                dataSource = None
                            else:
                                dataSource = sourceItemList[0]


                            parseItemSourceItem = ParseItemSourceList.gql("WHERE Parse=KEY('%(parse)s') AND SourceItem=KEY('%(source)s')" % {'parse':parsedSong.key(), 'source': dataSource.key() })
                            if parseItemSourceItem.count() == 0:
                                parseItemSourceItem = ParseItemSourceList(Parse = parsedSong, SourceItem = dataSource)
                                parseItemSourceItem.put()
                            logging.info('song could not be parsed: %(input)s' % {'input':parsedSong.InputString})

                        else:
                            logging.info('mp3 found in datastore.')
                            mp3Data.SourceUrl = sourceUrl
                            mp3Data.SongTitle = formatSongTitle(songTitle)
                            mp3Data.put()
                        hrefList.append( mp3href )
                    else:
                        logging.info("Could not parse data - no title found.  url: %s " % parseUrl)
                else:
                    logging.info("URL Fetch returned an error. %s" % page.status_code)
        except urlfetch.Error, e:
            errorMessage = '<li>error fetching URL %s</li>' % parseUrl
            errorOutput += errorMessage
            logging.error(errorMessage)
        except UnicodeEncodeError, e:
            errorMessage = '<li>not an HTML document at url: %s</li>' % parseUrl
            errorOutput += errorMessage
            logging.error(errorMessage)
    else:
        errorOutput = 'expected GET method'
        logging.error(errorOutput)
    htmlOutput = '''
    <html>
        <head>
            <title>Test playlist</title>
            <link type="text/css" href="/skin/jplayer.blue.monday.css" rel="stylesheet" />
            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js">
            </script>
        </head>
        <body>
            <h1>music</h1>
    '''
    for href in hrefList:
         htmlOutput += '<li><a href=\"' + str(href) + '">' + href + '</a></li>'

    if errorOutput != '':
        htmlOutput += '<h1>Errors</h1>'
        htmlOutput += '<ul>%s</ul>' % errorOutput

    htmlOutput += '''
        </body>
    </html>'''

    return HttpResponse('success')






