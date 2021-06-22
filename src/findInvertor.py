from scapy.all import ARP, Ether, srp
import scapy.config
import scapy.layers.l2
import scapy.route
import sys
import os
import math

def find_Invertor(target_ip):
    arp = ARP(pdst=target_ip)
    # ff:ff:ff:ff:ff:ff MAC address indicates broadcasting
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    # stack them
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=0)[0]
    # a list of clients, we will fill this in the upcoming loop
    for sent, received in result:
        if received.hwsrc[0:8]=="34:ea:e7" or received.hwsrc[0:8]=="98:d8:63":
            #print("IP=",received.psrc,"and MAC= ",received.hwsrc)
            return received.psrc

def long2net(arg):
    if (arg <= 0 or arg >= 0xFFFFFFFF):
        raise ValueError("illegal netmask value", hex(arg))
    return 32 - int(round(math.log(0xFFFFFFFF - arg, 2)))

def to_CIDR_notation(bytes_network, bytes_netmask):
    network = scapy.utils.ltoa(bytes_network)
    netmask = long2net(bytes_netmask)
    net = "%s/%s" % (network, netmask)
    if netmask < 16:
        return None
    return net

interface_to_scan=None
if os.geteuid() != 0:
    sys.exit(1)
for network, netmask, _, interface, address, _ in scapy.config.conf.route.routes:
    if interface_to_scan and interface_to_scan != interface:
        continue
    # skip loopback network and default gw
    if network == 0 or interface == 'lo' or address == '127.0.0.1' or address == '0.0.0.0':
        continue
    if netmask <= 0 or netmask == 0xFFFFFFFF:
        continue
    # skip docker interface
    if interface != interface_to_scan and interface.startswith('docker') or interface.startswith('br-'):
        continue
    net = to_CIDR_notation(network, netmask)
    if net:
        invIP=find_Invertor(net)
        if invIP!= None and invIP!=" ":
            print (invIP)
            sys.exit()
