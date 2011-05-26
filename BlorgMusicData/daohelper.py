from BlorgMusicData.dao import Dao

__author__ = 'abeaupre'

def artistRoleNamesToObjects(artistRoleMap):
    #for each of the listed artists, getoradd
    songKeyArtists = []
    for artistRole in artistRoleMap:
        roleType = artistRole['role']
        artistName = artistRole['name']
        artistItem = Dao.ArtistItem_GetOrAdd(artistName)
        if artistItem:
            songKeyArtists.append({'artistItem':artistItem, 'roleType': roleType})

    return songKeyArtists