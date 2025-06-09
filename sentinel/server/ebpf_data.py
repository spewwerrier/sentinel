from django.http import HttpResponse, HttpRequest, StreamingHttpResponse
from server import sock_incoming, send_socket
from django.views.decorators.csrf import csrf_exempt
from server.models import IPV4_Packet
import json
import time

# we send data we get from the udp port to the continuous stream
# https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events

def incoming(request: HttpRequest):
    def event_stream():
        while True:
            data, address = sock_incoming.recvfrom(4096)

            json_data = data.decode('utf-8')
            data = json.loads(json_data)

            fields = IPV4_Packet(
                saddr=data['ip'],
                pkt_size=data['packet'],
                port=data['port'],
                urg=data['urg']
            )

            IPV4_Packet.save(fields)

            yield f"data: {json_data}\n\n"

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
