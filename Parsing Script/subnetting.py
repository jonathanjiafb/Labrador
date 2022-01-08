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
#subnet = '10.168.19.174/18'
#subnet_start2end(subnet)
#print(ipv4_address)
#print(mask_len)

csv_file = 'IPv4subnets.csv'
csv_file2 = 'IPv4subnetsf.csv'
fields = []
rows = []
with open(csv_file2, 'w') as csvfile2:
    csvwriter = csv.writer(csvfile2)
    with open(csv_file) as csvfile:
        csvreader = csv.reader(csvfile)

        fields = next(csvreader)
        csvwriter.writerow(fields)
        for row in csvreader:
            start_addr, end_addr = subnet_start2end(row[0])
            row[1] = start_addr
            row[2] = end_addr
            csvwriter.writerow(row)

