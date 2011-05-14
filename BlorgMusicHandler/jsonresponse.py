import datetime
from django.core.serializers import json, serialize
from django.http import HttpResponse
from django.conf.urls.defaults import patterns

class JsonResponse(HttpResponse):
    def __init__(self, content, encoder=json.DjangoJSONEncoder(), *args, **kwargs):
        super(JsonResponse, self).__init__(encoder.encode(content), mimetype="text/json", *args, **kwargs)


class JsonWebService(object):
    '''
    Base class for json-based web services
    '''
    class JSONEncoder(json.DjangoJSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
                return obj.ctime()
            else:
                return json.DjangoJSONEncoder.default(self, obj)
            
    default_encoder = JSONEncoder()
    
    @staticmethod
    def jsonresponse(encoder=default_encoder):
        def decorator(func):
            def wrap_json(*args):
                ret = func(*args)
                return JsonResponse(ret, encoder=encoder)
            wrap_json._is_json_ws = True
            return wrap_json
        return decorator
    
    @classmethod
    def getActions(cls):
        '''
        returns the methods decorated with jsonresponse
        @param cls:
        '''
        return filter(lambda k: getattr(getattr(cls, k), '_is_json_ws', False), dir(cls))
    
    @property
    def urls(self):
        urls = []
        for action in self.getActions():
            urls.append((r'^json/' + action, getattr(self, action)))
        urlpatterns = patterns('', *urls)
        return urlpatterns
