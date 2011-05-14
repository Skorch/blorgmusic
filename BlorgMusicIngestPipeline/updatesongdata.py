#sys.path.append('py')
from django.http import HttpResponse, HttpResponseRedirect
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import re
import logging
#from domain import MusicItem
from BlorgMusicData.models import  *
from BlorgMusicHelper.stringhelper import  *



    
def generateCanonicalSongId(songTitle, songArtist, remixArtist, featuringArtist, mashupArtist, originalArtist):
    return "%(songtitle)s_%(songartist)s_%(remixartist)s_%(featuringartist)s_%(mashupartist)s_%(originalartist)s" % {'songtitle':songTitle, 'songartist':songArtist, 'remixartist': remixArtist, 'featuringartist':featuringArtist, 'mashupartist':mashupArtist, 'originalartist':originalArtist}

def main(request):
    logging.info('request object %s' % request)
    logging.info('songurl: %s' % request.REQUEST.get('songurl'))
    songUrl = str2none(request.REQUEST.get('songurl'))
    inputString = str2none(request.REQUEST.get('inputstring'))
    songTitle = str2none(request.REQUEST.get('songtitle'))
    songArtist = str2none(request.REQUEST.get('songartist'))
    sourceUrl = str2none(request.REQUEST.get('sourceurl'))
    sourceName = str2none(request.REQUEST.get('sourcename'))
    remixArtist = str2none(request.REQUEST.get('remixartist'))
    featuringArtist = str2none(request.REQUEST.get('featuringartist'))
    isMashup = request.REQUEST.get('ismashup') != ''
    originalArtist = str2none(request.REQUEST.get('originalartist'))
    songNotes = str2none(request.REQUEST.get('songnotes'))
    logging.info('song notes: "%s"' %songNotes)

    parseItemKey = str2none(request.REQUEST.get('parseitemkey'))
    if parseItemKey:
        parseItemKey = parseItemKey.strip()

    #TODO: validate minimum data requirements

    #write all of the artist information to the DB
    songArtistItem = ArtistItem.get_or_insert(key_name=toLowerAndStripPunct(songArtist), Name=songArtist)
    logging.info("Creating new Primary Artist : %s" % songArtist)
    songArtistItem.put()
    if remixArtist != None:
        remixArtistItem = ArtistItem.get_or_insert(key_name=toLowerAndStripPunct(remixArtist), Name=remixArtist)
        remixArtistItem.HasRemix = True
        logging.info("Creating new Remix Artist : %s" % remixArtist)
        remixArtistItem.put()
    if featuringArtist != None:
        featuringArtistItem = ArtistItem.get_or_insert(key_name=toLowerAndStripPunct(featuringArtist), Name = featuringArtist)
        featuringArtistItem.HasFeaturing = True
        logging.info("Creating new Featuring Artist : %s" % featuringArtist)
        featuringArtistItem.put()
    if originalArtist != None:
        originalArtistItem = ArtistItem.get_or_insert(key_name=toLowerAndStripPunct(originalArtist), Name = originalArtist)
        originalArtistItem.HasCover = True
        logging.info("Creating new Original Artist : %s" % originalArtist)
        originalArtistItem.put()


    #generate the key for the canonical song
    #canonicalSongId = generateCanonicalSongId(songTitle, songArtist, remixArtist, featuringArtist, mashupArtist, originalArtist)
    #Add song to canoical data store or get the existing reference
#        canonicalSongResult = SongItem.gql("WHERE SongArtist=KEY('%(songartist)s') AND SongTitle='%(songtitle)s'" % {'songartist':songArtistItem.key.id(), 'songtitle':songTitle})
    canonicalQuery = SongItem.all()
    canonicalQuery.filter('SongKey =', toLowerAndStripPunct(songTitle)).ancestor(songArtistItem)

    if canonicalQuery.count(limit=1) == 0:
        canonicalSong = SongItem(parent=songArtistItem) #the canonical Song record
        canonicalSong.SongKey = toLowerAndStripPunct(songTitle)
        canonicalSong.SongTitle = songTitle
        canonicalSong.SongArtist = songArtistItem
        canonicalSong.SongNotes = songNotes
        if 'remixArtistItem' in locals():
            canonicalSong.RemixArtist = remixArtistItem
        if 'featuringArtistItem' in locals():
            canonicalSong.FeaturingArtist = featuringArtistItem
        if 'isMashup' in locals():
            canonicalSong.IsMashup = isMashup
        if 'originalArtistItem' in locals():
            canonicalSong.OriginalArtist = originalArtistItem
        logging.info("Creating new Canonical Song: %s" % songTitle)
        canonicalSong.put()
    else:
        canonicalSong = canonicalQuery[0]

    sourceBlogPost = BlogPost.get_by_key_name(sourceUrl) #reference to the actual blog post
    #TODO:  if this is None then error

    songPostId = songUrl

    songPost = SongPost.get_by_key_name(songPostId)
    if songPost == None:
        #create a new reference
        songPost = SongPost(key_name=songPostId) #the reference to the song on the blog post
        songPost.SongUrl = songUrl
        songPost.CanonicalSong = canonicalSong
        songPost.Blog = sourceBlogPost
        songPost.OriginalText = inputString
        logging.info("Creating new Song Post : %s" % songPostId)

        songPost.put()

    #create a relationship between the source and the item.  This will be the initial concept of the Channels
    #dataSource = DataSource.get(sourceKey)
#TODO:check for existance

    parseItem = ParseItem.get(parseItemKey)


    #for each source associated with the Parse item, create a corresponding SongItemSourceItem object
    for sourceItem in parseItem.ParseItemSources:


        songPostDataSourceListQuery = SongPostDataSourceList.gql("WHERE SongPost=KEY('%(songpost)s') AND DataSource=KEY('%(datasource)s')" % {'songpost': songPost.key(), 'datasource': sourceItem.SourceItem.key()})
        if songPostDataSourceListQuery.count() == 0:
            logging.info('cannot find songPostDataSource, creating a new item')
            sourceList = SongPostDataSourceList(SongPost=songPost, DataSource=sourceItem.SourceItem)
            sourceList.put()
        else:
            logging.info('found an existing songPostDataSource item.  Not inserting')
        sourceItem.delete()

#once everything is succesful, remove the parseItem
    if parseItem != None:
        parseItem.delete()

    errorOutput = ''



    htmlOutput = '''
    <html>
        <head>
            <title>Song Updated</title>
        </head>
        <body>
            <h1>Song</h1>
            <ul>
            <li>Input String: %(inputstring)s</li>
            <li>Song Title: %(songtitle)s</li>
            <li>Song Artist: %(songartist)s</li>
            <li>Remix Artist: %(remixartist)s</li>
            <li>Featuring Artist: %(featuringartist)s</li>
            <li>Is Mashup: %(ismashup)s</li>
            <li>Original Artist: %(originalartist)s</li>
            <li>Song Url: %(songurl)s</li>
            <li>Source Url: %(sourceurl)s</li>

            </ul>
    '''% {
          'inputstring':inputString
          ,'songurl':songUrl
          ,'songtitle':songTitle
          ,'songartist':songArtist
          ,'sourceurl':sourceUrl
          ,'remixartist':remixArtist
          ,'featuringartist':featuringArtist
          ,'ismashup':isMashup
          ,'originalartist':originalArtist

          }

    htmlOutput += '''
        </body>
    </html>'''

    return HttpResponse(htmlOutput)


