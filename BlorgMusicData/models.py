__author__ = 'abeaupre'
from appengine_django.models import BaseModel
from google.appengine.ext import db

#Depricated - needs to be converted into the new structure
class MusicItem(db.Model):
    Url = db.StringProperty()
    Source = db.StringProperty()
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    ModifyTime = db.DateTimeProperty(auto_now=True)
    DataVersion = db.IntegerProperty(default=1)
    SongArtist = db.StringProperty() #the main artist for the current song
    SongTitle = db.StringProperty() #the title of the current song
    SourcelUrl = db.StringProperty()

    #the following should be references to an Artist object
    #for the moment, store the raw string
    RemixArtist = db.StringProperty() #remixed by
    OriginalAtist = db.StringProperty() #cover song
    MashupArtist = db.StringProperty() #This should be a string list
    FeaturingArtist = db.StringProperty() #featuring another artist

    OriginalText = db.StringProperty() #the original text around the link


#New canonical Structure
class ArtistItem(db.Model):
    Name = db.StringProperty(required=True)
    HasRemix = db.BooleanProperty(default=False)
    HasMashup = db.BooleanProperty(default=False)
    HasCover = db.BooleanProperty(default=False)
    HasFeaturing = db.BooleanProperty(default=False)
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    ModifyTime = db.DateTimeProperty(auto_now=True)
    DataVersion = db.IntegerProperty(default=1)


class SongItem(db.Model):
    SongKey = db.StringProperty() #a normalized version of the song name
    SongTitle = db.StringProperty() #the title of the current song
    SongArtist = db.ReferenceProperty(ArtistItem, collection_name="PrimarySongs") #the main artist for the current song
    RemixArtist = db.ReferenceProperty(ArtistItem, collection_name="RemixSongs") #remixed by
    OriginalArtist = db.ReferenceProperty(ArtistItem, collection_name="OriginalSongs") #cover song
    IsMashup = db.BooleanProperty(default=False)
    FeaturingArtist = db.ReferenceProperty(ArtistItem, collection_name="FeaturingSongs") #featuring another artist
    SongNotes = db.StringProperty() #other misc info in (brackets)
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    ModifyTime = db.DateTimeProperty(auto_now=True)
    DataVersion = db.IntegerProperty(default=1)


class DataSource(BaseModel):
    SourceName = db.StringProperty(required=True)
    SourceUrl = db.StringProperty(required=True)
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    ModifyTime = db.DateTimeProperty(auto_now=True)
    DataVersion = db.IntegerProperty(default=1)

class BlogSource(db.Model):
    BlogName = db.StringProperty(required=True)
    BlogUrl = db.StringProperty(required=True)
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    ModifyTime = db.DateTimeProperty(auto_now=True)
    DataVersion = db.IntegerProperty(default=1)

class BlogPost(db.Model):
    PostUrl = db.StringProperty(required=True)
    Summary = db.StringProperty()
    Blog = db.ReferenceProperty(BlogSource, collection_name="BlogPosts")
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    ModifyTime = db.DateTimeProperty(auto_now=True)
    DataVersion = db.IntegerProperty(default=1)

class SongPost(db.Model):
    SongUrl = db.StringProperty() #not required!  Support the ability to show blog posts where we couldn't strip the mp3 from
    CanonicalSong = db.ReferenceProperty(SongItem, collection_name="SongPosts")
    Blog = db.Reference(BlogPost, collection_name="BlogPosts")
    OriginalText = db.StringProperty() #the original text around the link
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    ModifyTime = db.DateTimeProperty(auto_now=True)
    DataVersion = db.IntegerProperty(default=1)

class SongPostDataSourceList(db.Model):
    SongPost = db.ReferenceProperty(SongPost, collection_name="DataSourceList")
    DataSource = db.ReferenceProperty(DataSource, collection_name="SongPostList")
    CreateTime = db.DateTimeProperty(auto_now_add=True)

class ParseItem(db.Model):
    InputString = db.StringProperty(required=True) #the original string from the web page
    SongArtist = db.StringProperty() #the main artist for the current song
    SongTitle = db.StringProperty() #the title of the current song
    RemixArtist = db.StringProperty() #remixed by
    OriginalArtist = db.StringProperty() #cover song
    SongNotes = db.StringProperty() #other misc info in (brackets)
    FeaturingArtist = db.StringProperty() #featuring another artist
    IsMashup = db.BooleanProperty(default=False) #is this a mashup?
    ParseSuccessful = db.BooleanProperty(default=False) #was this item successfully parsed
    CreateTime = db.DateTimeProperty(auto_now_add=True)
    ModifyTime = db.DateTimeProperty(auto_now=True)

    Url = db.StringProperty()
    SourceUrl = db.StringProperty()

class ParseItemSourceList(db.Model):
    Parse = db.ReferenceProperty(ParseItem, collection_name="ParseItemSources")
    SourceItem = db.ReferenceProperty(DataSource, collection_name="ParseItems")

      