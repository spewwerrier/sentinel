# Sentinel
Sentinel is a ebpf based ip filter with a web interface written using django.

To run this project first run the ebpf program which can be communicated using udp sockets.

```bash
sudo python ebpf/main.py
```

Next we need to run the web interface
```bash
virtualenv venv
. ./venv/bin/activate.fish # or any depending on the shell
python sentinel/manage.py runserver --noreload
```

The web interface now should be running in localhost:8000

The filter box is all purpose for now, it supports protocols and ip address based filtering
