from BlorgMusicData.dao import Dao
from django.http import HttpResponse
from google.appengine.api import urlfetch
from google.appengine.api.taskqueue import taskqueue
import re
import logging
import urlparse
from BlorgMusicData.models import  *

from xml.dom import minidom
from xml.parsers.expat import ExpatError

def generateTaskName(url, source):
    path = url.path.replace('/', '').replace('~', '')
    host = url.hostname.replace('.', '')

    return ('%(host)s-%(path)s-%(source)s' % {'host':host, 'path':path, 'source': source})[-500:]

def main(request):

    reLink = re.compile("((https?|ftp|file):\/\/[\-A-Z0-9+&@#\/%?=~_|!:,.;]*[\-A-Z0-9+&@#\/%=~_|])",re.IGNORECASE)
    parseUrlList = Dao.DataSource_GetListAll()


    errorOutput = ''
#        logging.info('Starting to fetch items from Twitter: %s items' % parseUrlList.count())
    hrefList = []
    for parseUrl in parseUrlList:
        logging.info('fetching twitter feed: %s' % parseUrl.SourceUrl)
        try:
            page = urlfetch.fetch(parseUrl.SourceUrl, headers = {'Cache-Control' : 'max-age=0'})
            logging.info(page)
            if page.status_code == 200:
                statusList = []
                try:
                    xmlDoc = minidom.parseString(page.content)
                    statusList = xmlDoc.getElementsByTagName('text')
                except ExpatError, e:
                    errorOutput += 'invalid Xml document.<BR>' + page.content
                for statusText in statusList:
                    reResult = reLink.search(statusText.childNodes[0].nodeValue)
                    r = reLink.findall(statusText.childNodes[0].nodeValue)
                    for linkText in r:
                        linkUrl = urlparse.urlparse(linkText[0])
                        logging.info('queueing url: %s' % linkUrl.geturl())
                        try:
#                                taskqueue.add( url='/fetchdata', params={'dataUrl':linkUrl.geturl(), 'dataSource': parseUrl.SourceName })
                            params={'dataUrl':linkUrl.geturl(), 'dataSource': parseUrl.SourceName }
                            #url = '/fetchdata/?dataUrl='+linkUrl.geturl()+'&dataSource='+parseUrl.SourceName
                            url = '/fetchdata/'
                            taskqueue.add( name=generateTaskName(linkUrl, parseUrl.SourceName), url=url, params=params, method='GET')
                            logging.info('get url: %s' % url)
                            logging.info('post data: %s' % params)
                            hrefList.append( linkUrl.geturl())
                        except taskqueue.TaskAlreadyExistsError, e:
                            errorOutput += '<li>%(sourcename)s - Duplicate task: %(taskname)s</li>' % {'sourcename': parseUrl.SourceName, 'taskname': generateTaskName(linkUrl, parseUrl.SourceName) }
                        except taskqueue.TombstonedTaskError, e:
                            errorOutput += '<li>%(sourcename)s - Tombstoned task: %(taskname)s</li>' % {'sourcename': parseUrl.SourceName, 'taskname': generateTaskName(linkUrl, parseUrl.SourceName) }


        except urlfetch.Error, e:
            errorMessage = '<li>error fetching URL %s</li>' % parseUrl
            errorOutput += errorMessage
            logging.error(errorMessage)



    htmlOutput = '''
    <html>
        <head>
            <title>Twitter Data Fetch</title>
        </head>
        <body>
            <h1>music</h1>
    '''
    for href in hrefList:
         htmlOutput += '<li><a href=\"' + str(href) + '">' + str(href) + '</a></li>'

    if errorOutput != '':
        htmlOutput += '<h1>Errors</h1>'
        htmlOutput += '<ul>%s</ul>' % errorOutput

    htmlOutput += '''
        </body>
    </html>'''

    return HttpResponse(htmlOutput)



