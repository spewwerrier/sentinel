# Sentinel
Sentinel is a ebpf based ip filter with a web interface written using django.

To run this project first run the ebpf program which can be communicated using udp sockets.

```bash
sudo python ebpf/main.py wlp3s0
```
wlp3s0 is a network interface, you can get yours using `ip a`. You can also create
your own virtual interfaces and attach to them. This also means creating a virtual machine and
attaching this program to vm's network should make this program monitor/block on vm's
network without affecting your network (Not verified but should work).

Next we need to run the web interface
```bash
virtualenv venv
. ./venv/bin/activate.fish # or any depending on the shell
python sentinel/manage.py runserver --noreload
```

The web interface now should be running in localhost:8000

The filter box is all purpose for now, it supports protocols and ip address based filtering
