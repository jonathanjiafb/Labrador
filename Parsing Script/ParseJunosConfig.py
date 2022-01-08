#!/usr/bin/python
import re
import pprint
import logging
import csv
import os

def parseJunosConf(text_body):

    list_of_vlan_database = re.findall(
        r"^(?:set vlans (\w*) description (?P<vlan_dsp>[\w\-\:+]*)\n)?set vlans (?P<vlan_name>\w*) vlan-id (?P<vlan_id>\d{1,4})\n(?:set vlans.*l3-interface irb\.(?P<irb_id>\d{1,4}))?",
        text_body, re.MULTILINE
    )

    list_of_phy_interfaces = re.findall(
        r"^set interfaces (?P<int_name>[^irb][\w\/\-\:]*) .*address (?:(?P<ip_v4>(?:\d{1,3}\.){3}\d{1,3}\/\d{1,2})|(?P<ipv6>(?:(?:[0-9a-fA-F]{1,4})\:){1,7}\:?[0-9a-fA-F]{1,4}\/\d{2,3}))",
        text_body, re.MULTILINE
    )

    list_of_irb_interfaces = re.findall(
        r"^set interfaces irb unit (\d{1,4}).*address (?:(?P<ip_v4>(?:\d{1,3}\.){3}\d{1,3}\/\d{1,2})|(?P<ipv6>(?:(?:[0-9a-fA-F]{1,4})\:){1,7}\:?[0-9a-fA-F]{1,4}\/\d{2,3}))",
        text_body, re.MULTILINE
    )

    phy_int_temp_dict = {}
    for row in list_of_phy_interfaces:
        if row[1]:
            phy_int_temp_dict[row[0]] = [row[1]]
        if row[2]:
            if row[0] in phy_int_temp_dict:
                phy_int_temp_dict[row[0]].append(row[2])
            else:
                phy_int_temp_dict[row[0]] = [None, row[2]]

    irb_int_temp_dict = {}
    for row in list_of_irb_interfaces:
        if row[1]:
            #if row[1] not in irb_int_temp_dict[row[0]]:
            irb_int_temp_dict[row[0]] = [row[1]]
        if row[2]:
            if row[0] in irb_int_temp_dict:
                if row[2] not in irb_int_temp_dict[row[0]]:
                    irb_int_temp_dict[row[0]].append(row[2])
            else:
                irb_int_temp_dict[row[0]] = [None, row[2]]

    return irb_int_temp_dict, phy_int_temp_dict, list_of_vlan_database

    #for item in list_of_vlan_database:
    #    print(item[3],"\t\t\t", item[2])
    # v_name     v_descrip        v_name        v_id    irb_n
    #'vlan206', 'OPEN-WIFI_HSS', 'vlan206',     '206',  '206'
    #'',            '',           'NTP_SERVER', '127',  '127'
    #pprint.pprint(phy_int_temp_dict)
    #pprint.pprint(irb_int_temp_dict)

file_dir = str(input("Please input the absolute path or relative path of the folder where all the Junos config files are stored:"))
all_files = os.listdir(file_dir)

output_csv = str(input("Please input the output csv file name(recommended format:date_site_type):"))
with open(output_csv, "w") as ivc:
    headers = [
        "vlan_id",          #0
        "vlan_description", #1
        "irb_ipv4",         #2
        "irb_ipv6",         #3
    ]

    csv_writer = csv.writer(ivc)
    csv_writer.writerow(headers)

    for conf_file in all_files:
        with open(file_dir + "/" + conf_file, "r") as f:
            config = f.read()
            irb_int_temp_dict, phy_int_temp_dict, list_of_vlan_database = parseJunosConf(config)


            for k in irb_int_temp_dict:
                i = 0
                while i < len(list_of_vlan_database):
                    if k == list_of_vlan_database[i][3]:
                        irb_int_temp_dict[k].insert(0,list_of_vlan_database[i][1])
                        list_of_vlan_database.pop(i)
                    i += 1
            #pprint.pprint(irb_int_temp_dict)

            for k in irb_int_temp_dict.keys():
                row = [k, None, None, None]
                i = 0
                while i < len(irb_int_temp_dict[k]):
                    row[i+1] = irb_int_temp_dict[k][i]
                    i += 1
                csv_writer.writerow(row)

            for k in phy_int_temp_dict.keys():
                row = [None, k, None, None]
                i = 0
                while i < len(phy_int_temp_dict[k]):
                    row[i+2] = phy_int_temp_dict[k][i]
                    i += 1
                csv_writer.writerow(row)

            pprint.pprint("Following vlans are created but w/o correlated IRB:"
                          "\nv_name     v_descrip        v_name        v_id    irb_n")
            for item in list_of_vlan_database:

                pprint.pprint(item)
