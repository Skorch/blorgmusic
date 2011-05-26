from BlorgMusicData.dao import *
from BlorgMusicData.daohelper import *
from django.test import TestCase
from models import *
from BlorgMusicIngestPipeline import parseinput, fetchdata

class DataItemTest(TestCase):

    def clearArtistItemData(self):
        for item in Dao.GetArtistItemList(1000, 1, 'id', True):
            Dao.DeleteArtistItem(item)

    def clearSongItemData(self):
        for item in Dao.SongItem_GetList(1000, 1, 'id', True):
            Dao.DeleteSongItem(item)

    def clearParseItemData(self):
        for item in Dao.GetParseItemList(1000, 1, 'id', True):
            Dao.DeleteParseItem(item)

    def addArtistItemData(self, name, hasCover, hasFeaturing, hasMashup, hasRemix):
        newArtist = ArtistItem()
        newArtist.Name = name
        newArtist.HasCover = hasCover
        newArtist.HasFeaturing = hasFeaturing
        newArtist.HasMashup = hasMashup
        newArtist.HasRemix = hasRemix
        newArtist.save()
        return newArtist

    def addSongPostData_FromParseData(self, parsedText, blogPostItem, songUrl):
        return Dao.SongPost_AddFromParseData(parsedText, songUrl, blogPostItem)

    def addBlogPostData(self, blogItem, blogPostUrl, blogPostSummary ):
        return Dao.BlogPost_GetOrInsert(blogPostUrl, blogPostSummary, blogItem)

    def addBlogSourceData(self, blogUrl, blogName):
        return Dao.BlogSource_GetOrInsert(blogUrl, blogName)
        
    def setUp(self):
        self.clearArtistItemData()
        self.addArtistItemData("Beastie Boys", False, False, False, False)
        self.addArtistItemData("Sleepy Sun", True, False, False, False)
        self.addArtistItemData("Tool", False, True, False, False)
        self.addArtistItemData("Queens of the Stone Age", False, False, True, False)
        self.addArtistItemData("UNKLE", False, False, False, True)

        self.addArtistItemData("Them Cooked Vultures", False, False, True, True)
        self.addArtistItemData("Nine Inch Nails", False, True, True, True)
        self.addArtistItemData("Junip", True, True, True, True)

        Dao.DataSource_GetOrAdd('unknown', 'http://unknown')

    def test_models(self):
        logging.info('unit test: test_models')
        self.assertTrue(ArtistItem.objects.count() > 0, "True")
        self.assertTrue(SongItem.objects.count() > 0, "True")

    def test_SongPostFromParse(self):
        inputString = self.getInputString()

        parsedData = parseinput.ParseInput.ParseSongTitle(inputString, True)

        self.assertTrue(parsedData)
        self.assertTrue(parsedData['successful'])
        self.assertTrue(len(parsedData['artistRoleList']) > 0 )

        dataSourceItem = Dao.DataSource_GetOrAdd('unknown', 'unkown')
        blogSourceItem = self.addBlogSourceData('http://www.indieshuffle.com', 'Indie Shuffle')
        blogPostItem = self.addBlogPostData(blogSourceItem, 'http://', 'Test Summary')

        songPost = Dao.SongPost_AddFromParseData(parsedData,  'htp://song/mp3.mp3', blogPostItem)
        self.assertTrue(songPost)
        
        self.assertTrue(songPost.CanonicalSong)


    def test_SongParse(self):
        inputArtist = 'Beastie Boys'
        inputTitle = 'Shake Your Rump'
        inputRemix = 'DJ Shadow'
        inputString = inputArtist + ' - ' + inputTitle + ' (' + inputRemix + ' remix)'
        parsedData = parseinput.ParseInput.ParseSongTitle(inputString, True)

        self.assertTrue(parsedData['successful'])
        self.assertTrue(parsedData['primaryArtist'] == inputArtist )
        self.assertTrue(parsedData['songTitle'] == inputTitle)
        self.assertTrue(len(parsedData['artistRoleList']) > 0 )


        inputString = "Beastie Boys - Intergalactic (Imperial Mix)"
        parsedData = parseinput.ParseInput.ParseSongTitle(inputString, True)
        self.assertTrue(parsedData)
        self.assertTrue(not parsedData['successful'])

        parseItem = Dao.AddParseItem(parsedData)
        self.assertTrue(parseItem)

        dataSource = Dao.GetDataSource('unknown')
        self.assertTrue(dataSource)
        Dao.AddParseItemSourceItemList(parseItem, dataSource)
        parseList = Dao.GetParseItemList(1000, 1, 'id', True)
        self.assertTrue(len(parseList) > 0)

    def test_SongKey(self):
        inputArtist = 'Beastie Boys'
        inputTitle = 'Shake Your Rump'
        inputRemix = 'DJ Shadow'
        inputString = inputArtist + ' - ' + inputTitle + ' (' + inputRemix + ' remix)'
        parsedData = parseinput.ParseInput.ParseSongTitle(inputString, True)
        self.assertTrue(parsedData)
        artistRoleList = artistRoleNamesToObjects(parsedData['artistRoleList'])

        songKey = Dao.generateSongKey(parsedData['songTitle'], artistRoleList)

        self.assertTrue(songKey == "shake your rump_13,21")

    def test_SongTitleFormat(self):
        inputString = self.getInputString()
        parsedData = parseinput.ParseInput.ParseSongTitle(inputString, True)
        self.assertTrue(parsedData)

        songTitle = parsedData['songTitle']
        songNote = parsedData['songNote']
        artistRoleList = parsedData['artistRoleList']
        songTitleFormatted = formatSongTitle(inputTitle, songNote, artistRoleList)

        self.assertTrue(songTitleFormatted == inputString)


    @classmethod
    def getInputString(cls):
        inputArtist = 'Beastie Boys'
        inputTitle = 'Shake Your Rump'
        inputRemix = 'DJ Shadow'
        inputString = inputArtist + ' - ' + inputTitle + ' (' + inputRemix + ' Remix)'
        return inputString

    def test_fetchData(self):
        blogItem = Dao.BlogSource_GetOrInsert('http://www.indieshuffle.com', 'Indie Shuffle')
        blogPostUrl = 'http://www.indieshuffle.com/#:/the-cure-lovesong-diplo-remix/'
        blogPostItem = Dao.BlogPost_GetOrInsert(blogPostUrl, 'Test', blogItem)
        dataSource = 'unknown'
        fetchdata.fetchSongData(blogPostUrl, dataSource)

        blogPostItem = Dao.BlogPost_Get(blogPostUrl)

        self.assertTrue(blogPostItem)
