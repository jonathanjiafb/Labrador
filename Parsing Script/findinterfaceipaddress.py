#!/usr/bin/python
import os
import re

all_files = os.listdir('20211104/')
#print(all_files)
ipv4_address = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}')
ipv6_address = re.compile(r'(([0-9a-fA-F]{1,4})\:){1,7}\:[0-9a-fA-F]{1,4}\/\d{2,3}')
count = 0
print('#'*40 + '\n' + 'Following are IPv4 Subnets' + '\n' + '#'*40)
for file in all_files:
    with open('20211104/' + file) as f:
        for line in f:
            if line.startswith('  ip address'):
                if ipv4_address.search(line):
                    print(ipv4_address.search(line)[0])
print('#'*40 + '\n' + 'Following are IPv6 Subnets' + '\n' + '#'*40)
for file in all_files:
    with open('20211104/' + file) as f:
        for line in f:
            if line.startswith('  ipv6 address'):
                if ipv6_address.search(line):
                    print(ipv6_address.search(line)[0])