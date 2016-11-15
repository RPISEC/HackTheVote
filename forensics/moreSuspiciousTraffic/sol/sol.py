import dpkt
import morse_talk

pcap = dpkt.pcapng.Reader(open('../handout/SecureFloridaVotingBoothTraffic.pcapng'))

last_ts = 1477356338.61
ctr = 0
morse = ''
for ts,pkt in pcap:
    # Only look at useful UDP packets
    eth = dpkt.ethernet.Ethernet(pkt)
    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
        continue
    ip = eth.data
    if ip.p != dpkt.ip.IP_PROTO_UDP:
        continue
    udp = ip.data
    if 23284 not in [udp.sport, udp.dport]:
        continue
    # Check the timestamps to differentiate morse code
    dif = ts-last_ts
    if  dif < 0.1:
        ctr +=1
    elif dif > 0.48:
        if ctr == 6:
            morse += '.'
        elif ctr == 12:
            morse += '-'
        if dif > 1:
            morse += ' '
        ctr = 1
        last_ts = ts

# Print morse and flag
print morse
flag = ''
for i in morse.split(' '):
    try:
        flag += morse_talk.decode(i)
    except KeyError:
        flag += '?'
print flag
