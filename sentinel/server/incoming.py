from django.http import HttpResponse, HttpRequest, StreamingHttpResponse
from django.template import loader
import time

def index(request: HttpRequest):
    def event_stream():
        while True:
            yield f"data: hello world\n\n"
            time.sleep(1)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    
    return response 
