// TODO: since skb_buff works with bcc try dropping the packet in skb_buff
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/in.h>
#include <linux/in6.h>
#include <linux/ip.h>
#include <linux/ipv6.h>
#include <linux/tcp.h>
#include <linux/types.h>

struct ipv4_pkt {
  __be32 saddr;
  __u32 pkt_size;
  __u16 port;
  __u16 urg;
};

struct ipv6_addr {
  __u64 high;
  __u64 low;
};

struct ipv6_pkt {
  struct in6_addr saddr;
  __u32 pkt_size;
  __u16 port;
  __u16 urg;
} __attribute__((packed));

BPF_HASH(blacklist_ipv4, __be32, bool);
BPF_HASH(blacklist_ipv6, struct ipv6_addr, bool);
BPF_HASH(blacklist_protocol, u8, bool);

BPF_RINGBUF_OUTPUT(incoming_ipv4, 1 << 4);
BPF_RINGBUF_OUTPUT(incoming_ipv6, 1 << 4);

BPF_RINGBUF_OUTPUT(blocked_ipv4, 1 << 4);
BPF_RINGBUF_OUTPUT(blocked_ipv6, 1 << 4);

int handle_rx(struct xdp_md *ctx) {
  void *data = (void *)(long)ctx->data;
  void *data_end = (void *)(long)ctx->data_end;
  __u32 data_len = data_end - data;

  struct ethhdr *eth = data;
  if ((void *)(eth + 1) > data_end) {
    return XDP_PASS;
  }

  // ipv4
  if (bpf_ntohs(eth->h_proto) == ETH_P_IP) {
    struct iphdr *ip = (void *)(data + sizeof(struct ethhdr));
    if ((void *)(eth + 1) + sizeof(struct iphdr) > data_end) {
      return XDP_PASS;
    }

    struct tcphdr *tcp = (void *)ip + (ip->ihl * 4);
    if ((void *)tcp + sizeof(*tcp) > data_end) {
      return XDP_PASS;
    }

    __be32 saddr = ip->saddr;
    _Bool *elem = blacklist_ipv4.lookup(&saddr);

    struct ipv4_pkt pkt;
    pkt.pkt_size = data_len;
    pkt.saddr = saddr;
    pkt.port = bpf_ntohs(tcp->source);
    pkt.urg = bpf_ntohs(tcp->urg);

    // https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
    if (blacklist_protocol.lookup(&ip->protocol)) {
      blocked_ipv4.ringbuf_output(&pkt, sizeof(pkt), 0);
      return XDP_DROP;
    }

    if (elem != NULL) {
      // rb type blocked
      blocked_ipv4.ringbuf_output(&pkt, sizeof(pkt), 0);
      return XDP_DROP;
    }
    // rb type logs
    incoming_ipv4.ringbuf_output(&pkt, sizeof(pkt), 0);
    return XDP_PASS;
  }

  // ipv6
  if (bpf_ntohs(eth->h_proto) == ETH_P_IPV6) {

    struct ipv6hdr *ip = (void *)(data + sizeof(struct ethhdr));
    if ((void *)(eth + 1) + sizeof(struct ipv6hdr) > data_end) {
      return XDP_PASS;
    }

    struct tcphdr *tcp = (void *)ip + sizeof(struct ipv6hdr);
    if ((void *)tcp + sizeof(*tcp) > data_end) {
      return XDP_PASS;
    }
    
    struct in6_addr saddr = ip->saddr;
    struct ipv6_addr map_key;

    map_key.high =
        ((__u64)saddr.s6_addr[0] << 56) | ((__u64)saddr.s6_addr[1] << 48) |
        ((__u64)saddr.s6_addr[2] << 40) | ((__u64)saddr.s6_addr[3] << 32) |
        ((__u64)saddr.s6_addr[4] << 24) | ((__u64)saddr.s6_addr[5] << 16) |
        ((__u64)saddr.s6_addr[6] << 8) | ((__u64)saddr.s6_addr[7]);

    map_key.low =
        ((__u64)saddr.s6_addr[8] << 56) | ((__u64)saddr.s6_addr[9] << 48) |
        ((__u64)saddr.s6_addr[10] << 40) | ((__u64)saddr.s6_addr[11] << 32) |
        ((__u64)saddr.s6_addr[12] << 24) | ((__u64)saddr.s6_addr[13] << 16) |
        ((__u64)saddr.s6_addr[14] << 8) | ((__u64)saddr.s6_addr[15]);

    struct ipv6_pkt pkt;
    pkt.pkt_size = data_len;
    pkt.saddr = saddr;
    pkt.port = bpf_ntohs(tcp->source);
    pkt.urg = bpf_ntohs(tcp->urg);

    // https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
    if (blacklist_protocol.lookup(&ip->nexthdr)) {
      blocked_ipv6.ringbuf_output(&pkt, sizeof(pkt), 0);
      return XDP_DROP;
    }

    _Bool *elem = blacklist_ipv6.lookup(&map_key);
    if (elem != NULL && *elem) {
      // rb type blocked
      blocked_ipv6.ringbuf_output(&pkt, sizeof(pkt), 0);
      return XDP_DROP;
    }
    // rb type logs
    incoming_ipv6.ringbuf_output(&pkt, sizeof(pkt), 0);
    return XDP_PASS;
  }

  return XDP_PASS;
}
