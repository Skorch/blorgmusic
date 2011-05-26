
__author__ = 'abeaupre'

from BlorgMusicData.dao import *
from BlorgMusicData.daohelper import *
from django.test import TestCase
from BlorgMusicIngestPipeline import *

class DataItemTest(TestCase):

    def test_fetchData(self):
        blogItem = Dao.BlogSource_GetOrInsert('http://www.indieshuffle.com', 'Indie Shuffle')
        blogPostUrl = 'http://www.indieshuffle.com/#:/the-cure-lovesong-diplo-remix/'
        blogPostItem = Dao.BlogPost_GetOrInsert(blogPostUrl, 'Test', blogItem)
        dataSource = 'unknown'
        fetchdata.fetchSongData(blogPostUrl, dataSource)

        blogPostItem = Dao.BlogPost_Get(blogPostUrl)

        self.assertTrue(blogPostItem)
