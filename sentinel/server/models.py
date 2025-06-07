from django.db import models

class IPV4_Packet(models.Model):
 saddr=models.CharField(max_length=20)
 pkt_size=models.BigIntegerField()
 port=models.PositiveSmallIntegerField()
 urg=models.PositiveSmallIntegerField()

 def __str__(self):
  return f"Packet from {self.saddr} - size:{self.pkt_size}"
