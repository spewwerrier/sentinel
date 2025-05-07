from django.http import HttpResponse, HttpRequest, StreamingHttpResponse
from server import sock_incoming
import time

def incoming(request: HttpRequest):
    def event_stream():
        while True:
            data, address = sock_incoming.recvfrom(4096)
            yield f"data: {data.decode('utf-8')}\n\n"

            time.sleep(0.1)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    
    return response 

def blocked(request: HttpRequest):
    def event_stream():
        while True:
            data, address = sock_incoming.recvfrom(4096)
            yield f"data: {data.decode('utf-8')}\n\n"

            time.sleep(0.1)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    
    return response 
