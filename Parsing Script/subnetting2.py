#!/usr/bin/python
#import os
import re
import ipaddress
import csv

def subnet_start2end(subnet):
    intf = ipaddress.IPv4Interface(subnet)
    network = intf.network
    host = str(intf.hostmask)
    ipv4_addr = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    start_addr = ipv4_addr.search(str(network))[0]
    end_addr = str(int(start_addr.split('.')[0]) + int(host.split('.')[0])) +'.'+ \
               str(int(start_addr.split('.')[1]) + int(host.split('.')[1])) +'.'+  \
               str(int(start_addr.split('.')[2]) + int(host.split('.')[2])) +'.'+  \
               str(int(start_addr.split('.')[3]) + int(host.split('.')[3]))
    return start_addr, end_addr

csv_file = 'IPv4subnets.csv'
csv_file2 = 'IPv4subnetsf.csv'
fields = []
subnet_dic = {}
rows = ()
ip_block = []
with open(csv_file) as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        start_addr, end_addr = subnet_start2end(row[0])
        rows = (start_addr, end_addr)
        if rows not in subnet_dic :
            subnet_dic[rows] = row[0]

for key in subnet_dic.keys():
    ip_block.append(key)

def split_ip(ip):
    """Split an IP address given as string into a 4-tuple of integers."""
    return tuple(int(part) for part in ip.split('.'))

def my_key(item):
    return split_ip(item[0])

items = sorted(ip_block, key=my_key)

with open(csv_file2, 'w') as csvfile2:
    csvwriter = csv.writer(csvfile2)
    csvwriter.writerow(['start_addr', 'end_addr'])
    for item in items:
        csvwriter.writerow(item)
