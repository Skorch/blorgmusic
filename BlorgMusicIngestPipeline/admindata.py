from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime, date, time
import re
from BlorgMusicHelper.stringhelper import  *
from BlorgMusicData.models import *
from django.http import HttpResponse, HttpResponseRedirect



def main(request):
    datalist = ParseItem.all()
    htmlOutput = '''
        <html>
            <head>
                <title>Data Admin</title>
                <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js">
                </script>
                <script type="text/javascript" src="http://github.com/malsup/form/raw/master/jquery.form.js">
                </script>

            </head>


            <body>
                <h1>Set Song Info</h1>
            '''
    formNumber = 0
    for item in datalist:
        htmlOutput += '''
        <p>
        <form id="form_%(formnumber)s" class="songadmin" name="update_song" method="get" action="/updatesongdata/">
            <li class="songurl"><a href="%(url)s" target="_blank">%(original)s</a><input type="hidden" name="inputstring" value="%(original)s" /><input type="hidden" name="songurl" value="%(url)s" /></li>
            <li class="sourceurl">Source Url: <a href="%(sourceurl)s" target="_blank">%(sourceurl)s <input type="hidden" name="sourceurl" value="%(sourceurl)s" /></a></li>
            <li class="songartist">Artist: <input type="text" name="songartist" value="%(artistname)s" /></li>
            <li class="songtitle">Title: <input type="text" name="songtitle" value="%(songtitle)s" /></li>
            <li class="remixartist">Remix By: <input type="text" name="remixartist" value="%(remixartist)s" /></li>
            <li class="ismashup">IsMashup: <input type="checkbox" name="ismashup" value="%(ismashup)s" /></li>
            <li class="featuringartist">Featuring: <input type="text" name="featuringartist" value="%(featartist)s" /></li>
            <li class="originalartist">Original By: <input type="text" name="originalartist" value="%(originalartist)s" /></li>
            <li class="songnotes">Notes: <input type="text" name="songnotes" value="%(songnotes)s" /></li>
            <input type="hidden" name="parseitemkey" value="%(parseitemkey)s" />

            <input type="submit" />
        </form>
        </p>
        ''' % {
                 'formnumber':formNumber
               , 'original':item.InputString
               , 'url':xstr(item.Url)
               , 'sourceurl':xstr(item.SourceUrl)
               , 'artistname':xstr(item.SongArtist)
               , 'songtitle':xstr(item.SongTitle)
               , 'remixartist':xstr(item.RemixArtist)
               , 'ismashup':item.IsMashup
               , 'featartist':xstr(item.FeaturingArtist)
               , 'originalartist':xstr(item.OriginalArtist)
               , 'parseitemkey':item.key()
               , 'songnotes':xstr(item.SongNotes)
                }
        formNumber += 1
    htmlOutput += '''

            <script type="text/javascript">

                // wait for the DOM to be loaded
                $(document).ready(function() {
                    var options = {
                            //target:        '#output1',   // target element(s) to be updated with server response
                            beforeSubmit:  showRequest,  // pre-submit callback
                            success:       showResponse  // post-submit callback

                            // other available options:
                            //url:       url         // override for form's 'action' attribute
                            //type:      get        // 'get' or 'post', override for form's 'method' attribute
                            //dataType:  null        // 'xml', 'script', or 'json' (expected server response type)
                            //clearForm: true        // clear all form fields after successful submit
                            //resetForm: true        // reset the form after successful submit

                            // $.ajax options can be used here too, for example:
                            //timeout:   3000
                        };


                        $('form').ajaxForm(options);

                });

                // pre-submit callback
                function showRequest(formData, jqForm, options) {
                    // formData is an array; here we use $.param to convert it to a string to display it
                    // but the form plugin does this for you automatically when it submits the data
                    var queryString = $.param(formData);

                    // jqForm is a jQuery object encapsulating the form element.  To access the
                    // DOM element for the form do this:
                    // var formElement = jqForm[0];


                    // here we could return false to prevent the form from being submitted;
                    // returning anything other than false will allow the form submit to continue
                    return true;
                }
                function showResponse(responseText, statusText, xhr, $form)
                {
                    // for normal html responses, the first argument to the success callback
                    // is the XMLHttpRequest object's responseText property

                    // if the ajaxForm method was passed an Options Object with the dataType
                    // property set to 'xml' then the first argument to the success callback
                    // is the XMLHttpRequest object's responseXML property

                    // if the ajaxForm method was passed an Options Object with the dataType
                    // property set to 'json' then the first argument to the success callback
                    // is the json data object returned by the server
                 $form.remove()

//                        alert('status: ' + statusText + '\\n\\nresponseText: \\n' + responseText + 
//                            '\\n\\nThe output div should have already been updated with the responseText.');                     

                }
            </script>

            </body>
        </html>
        '''

    return HttpResponse(htmlOutput)



