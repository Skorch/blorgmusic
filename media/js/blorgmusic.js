

function getArtistInfo(artistKey)
{
	$.ajax({
		url: '/ws/json/ArtistSongs/',
		data: 'artistkey='+artistKey,
		success: processGetArtistInfo,
		result: "json"
	})
	
}

function processGetArtistInfo(data)
{
	songArtist = data[0].SongArtist.Name;
	result = '<em>More Song By ' + songArtist + '</em>';
	result += '<ul>';
	
	for( var i = 0; i < data.length; i++)
	{
		result += "<li>" + data[i].SongTitle + "</li>"

	}
	
	result += "</l>";
	
	$("#moresongs").html(result);
}


function addAllToQueue()
{
    console.log('add to queue');
    $("#musicstream li").each(function(item){
        var newQueueItem = $(this).clone(true).appendTo("#songqueue");
        newQueueItem.find("a").addClass("sm2_button");
        newQueueItem.find("a").removeClass("songitem");
    });

}
function clearQueue()
{
    $("#songqueue li").remove();
}

function getSongStream(direction, page, size, source)
{
    //var stream = $(this).parents("div.songstream");
    stream = $("div.songstream:first");
    if(!page){
        page = parseInt(stream.attr("page"));
    }
    if(!size){
        size = parseInt(stream.attr("size"));
    }
    if(!source){
        source = stream.attr("source");        
    }

    if(isNaN(size))
        size = 50;

    if(isNaN(page))
        page=1;

    if(direction == "prev")
    {
        if(page>1)
        {
            page--;
        }
    }
    else
    {
        page++;
    }

	$.ajax({
		url: '/ws/json/SongStream/',
		data: {'src': source, 'p': page, 's': size},
		result: "html",
        context:stream,
        success: function(data){
            $(this).replaceWith($(data));

        } 
    });

}