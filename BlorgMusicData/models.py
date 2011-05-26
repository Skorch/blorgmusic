__author__ = 'abeaupre'
from django.db import models



#New canonical Structure
class ArtistItem(models.Model):
    Name = models.CharField(blank=False, null=False, max_length=50)
    HasRemix = models.BooleanField(blank=False, null=False)
    HasMashup = models.BooleanField(blank=False, null=False)
    HasCover = models.BooleanField(blank=False, null=False)
    HasFeaturing = models.BooleanField(blank=False, null=False)
    CreateTime = models.DateTimeField(auto_now_add=True)
    ModifyTime = models.DateTimeField(auto_now_add=True, auto_now=True)
    DataVersion = models.IntegerField(blank=False, null=False, default=1) 

    def __str__(self):
        return self.Name

class SongArtistRoleList(models.Model):
    SONGARTISTROLECHOICES = (
        ('P', 'Primary'),
        ('R', 'Remix'),
        ('F', 'Featuring'),
        ('O', 'Original'),
        ('M', 'Mashup'),
    )
    Song = models.ForeignKey('SongItem')
    Artist = models.ForeignKey('ArtistItem')
    Role = models.CharField(blank=False, null=False, choices=SONGARTISTROLECHOICES, max_length=20)

class SongItem(models.Model):
    SongKey = models.CharField(blank=False, null=False, max_length=50) #a normalized version of the song name
    PrimaryArtist = models.ForeignKey('ArtistItem', null=False, blank=False)
    SongTitle = models.TextField(blank=False, null=False) #the title of the current song
    FormattedSongTitle = models.TextField(blank=False, null=False) #the de-normalized representation of the song title including all artists
#TODO:  Expand on this:  include isRemix, isCover, etc
#    IsMashup = models.BooleanField(default=False, null=False, blank=False)
    SongNotes = models.TextField(blank=True, null=True) #other misc info in (brackets)
    CreateTime = models.DateTimeField(auto_now_add=True)
    ModifyTime = models.DateTimeField(auto_now_add=True, auto_now=True)
    DataVersion = models.IntegerField(blank=False, null=False, default=1)

    ArtistRoleList = []

    def __str__(self):
        return self.SongTitle


class DataSource(models.Model):
    SourceName = models.CharField(blank=False, null=False, max_length=50)
    SourceUrl = models.CharField(blank=False, null=False, max_length=256)
    CreateTime = models.DateTimeField(auto_now_add=True)
    ModifyTime = models.DateTimeField(auto_now_add=True, auto_now=True)
    DataVersion = models.IntegerField(blank=False, null=False, default=1)

class BlogSource(models.Model):
    BlogName = models.CharField(blank=False, null=False, max_length=50)
    BlogUrl = models.CharField(blank=False, null=False, max_length=256)
    CreateTime = models.DateTimeField(auto_now_add=True)
    ModifyTime = models.DateTimeField(auto_now_add=True, auto_now=True)
    DataVersion = models.IntegerField(blank=False, null=False, default=1)

class BlogPost(models.Model):
    PostUrl = models.CharField(blank=False, null=False, max_length=256)
    Summary = models.TextField(blank=False, null=False)
    Blog = models.ForeignKey('BlogSource')
    CreateTime = models.DateTimeField(auto_now_add=True)
    ModifyTime = models.DateTimeField(auto_now_add=True, auto_now=True)
    DataVersion = models.IntegerField(blank=False, null=False, default=1)

class SongPost(models.Model):
    SongUrl = models.CharField(blank=False, null=False, max_length=256)
    CanonicalSong = models.ForeignKey('SongItem')
    Blog = models.ForeignKey('BlogPost')
    OriginalText = models.TextField(blank=True, null=True)
    CreateTime = models.DateTimeField(auto_now_add=True)
    ModifyTime = models.DateTimeField(auto_now_add=True, auto_now=True)
    DataVersion = models.IntegerField(blank=False, null=False, default=1)

class SongPostDataSourceList(models.Model):
    SongPost = models.ForeignKey('SongPost')
    DataSource = models.ForeignKey('DataSource')
    CreateTime = models.DateTimeField(auto_now_add=True)
    ModifyTime = models.DateTimeField(auto_now_add=True, auto_now=True)
    DataVersion = models.IntegerField(blank=False, null=False, default=1)

class ParseItem(models.Model):

    InputString = models.CharField(null=False, blank=False, unique=True, max_length=256) #the original string from the web page
#    SongArtist = models.CharField() #the main artist for the current song
#    SongTitle = models.CharField() #the title of the current song
#    RemixArtist = models.CharField() #remixed by
#    OriginalArtist = models.CharField() #cover song
#    SongNotes = models.CharField() #other misc info in (brackets)
#    FeaturingArtist = models.CharField() #featuring another artist
#    IsMashup = models.BooleanField(default=False) #is this a mashup?
#    ParseSuccessful = models.BooleanField(default=False) #was this item successfully parsed
    CreateTime = models.DateTimeField(auto_now_add=True)
    ModifyTime = models.DateTimeField(auto_now_add=True, auto_now=True)
    DataVersion = models.IntegerField(blank=False, null=False, default=1)

    Url = models.TextField()
    SourceUrl = models.TextField()

class ParseItemSourceList(models.Model):    
    Parse = models.ForeignKey('ParseItem')
    SourceItem = models.ForeignKey('DataSource')

      