from django.http import HttpResponse, HttpRequest, StreamingHttpResponse
from server import sock_incoming, send_socket
from django.views.decorators.csrf import csrf_exempt
import time

# we send data we get from the udp port to the continuous stream
# https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events


def incoming(request: HttpRequest):
    # TODO: save these value in open database connection
    def event_stream():
        while True:
            data, address = sock_incoming.recvfrom(4096)
            yield f"data: {data.decode('utf-8')}\n\n"

            time.sleep(0.1)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"

    return response


@csrf_exempt
def filter(request: HttpRequest):
    req = request.POST
    data = req["ipstring"]
    send_socket.sendto(data.encode("utf-8"), ("localhost", 7779))
    return HttpResponse("filtered")
