function createPlaylist( fileList )
{
	var audioPlaylist = new Playlist("1", [fileList], {
			ready: function() {
				audioPlaylist.displayPlaylist();
				audioPlaylist.playlistInit(false); // Parameter is a boolean for autoplay.
			},
			ended: function() {
				audioPlaylist.playlistNext();
			},
			play: function() {
				$(this).jPlayer("pauseOthers");
			},
			swfPath: "/media/player/swf",
			supplied: "mp3"
		});
		
	return audioPlaylist
}