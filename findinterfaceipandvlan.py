#!/usr/bin/python
import os
import re
import csv
file_dir = str(input('Please input the folder where all the config files are stored:'))
all_files = os.listdir(file_dir)
ipv4_address = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}')
ipv6_address = re.compile(r'(([0-9a-fA-F]{1,4})\:){1,7}\:[0-9a-fA-F]{1,4}\/\d{2,3}')
vlan_f = "^vlan \d{1,4}\n  name ([\w-_\.]+)?"
vlan_r = {}
with open('ipvlan.csv', 'w') as ivc:
    csvwriter = csv.writer(ivc)
    csvwriter.writerow(['VLAN_DBNUMBER','VLAN_IFNUMBER', 'VLAN_NAME', 'IP_PREFIX'])
    for conf_file in all_files:
        with open(file_dir + '/'+ conf_file,'r') as f:
            config = f.read()
            conf_v = re.findall(r'vlan \d{1,4}\n  name [\w\-\.]+', config)
            for item_v in conf_v:
                vlan_n = re.search(r'\d{1,4}',item_v).group()
                vlan_d = re.findall(r'name ([\w\-\.\/]+)', item_v)
                vlan_r[vlan_n] = vlan_d[0]
                #print(vlan_r)
            conf_i = re.findall(r'interface Vlan(\d{1,4})\n(  .*\n)*  ip address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})', config)
            for item_i in conf_i:
                #print(item_i[0],item_i[2])
                if item_i[0] in vlan_r.keys():
                    new_item = [item_i[0],item_i[0], vlan_r[item_i[0]], item_i[2]]
                    #print(new_item)
                    csvwriter.writerow(new_item)
                    vlan_r.pop(item_i[0])
                else:
                    new_item = ['None',item_i[0], 'None', item_i[2]]
                    csvwriter.writerow(new_item)
            for (k,v) in vlan_r.items():
                new_item = [k, 'None', v, 'None']
                csvwriter.writerow(new_item)

