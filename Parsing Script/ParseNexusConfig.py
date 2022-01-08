#!/usr/bin/python
import re
import os
import pprint
import logging
import csv
import io


def parseNexusConf(text_body):
    list_of_block_of_vlan_interfaces = re.findall(
        r"(^interface Vlan.*(\n[^\n]+)*\n)", text_body, re.MULTILINE
    )

    vlan_interface_facts = [  # list comprehension
        {
            "vlan_id": int(re.search(r"\d+", interface[0].splitlines()[0]).group()),
            "vlan_intr_name": re.search(r"description (.+)", interface[0])
            and re.search(r"description (.+)", interface[0]).group(1),
            "ipv4": re.findall(r"ip address (.+)", interface[0]),
            "ipv6": re.findall(r"ipv6 address (.+)", interface[0]),
        }
        for interface in list_of_block_of_vlan_interfaces
    ]


    list_of_block_of_vlan_database = re.findall(
        r"(^vlan [\d,-]+(\n  .+)?)", text_body, re.MULTILINE
    )


    def decompression_func(number_with_maybe_hyphen):
        # 1,2-4,5 or 1
        maybe_first_last_pairs = number_with_maybe_hyphen.split(",")
        # ["1", "2-4", "5"] or ["1"]
        # if len(maybe_first_last_pairs) == 1: # ["1000"]
        #    return [int(x) for x in maybe_first_last_pairs] # makes int
        # ["1", "2-4", "5"]
        acc = []
        for el in maybe_first_last_pairs:
            if "-" in el:  # "1-3"
                first, last = el.split("-")
                # put them in one at a time
                acc = acc + list(range(int(first), int(last) + 1))
            else:  # "1"
                acc.append(int(el))
        return acc


    vlan_db_facts_intermediate = [
        {
            "vlan_ids": decompression_func(re.search(r"[\d\-\,]+", vlan_info[0]).group(0)),
            "vlan_db_name": re.search(r"name (.*)", vlan_info[0])
            and re.search(r"name (.*)", vlan_info[0]).group(1),
        }
        for vlan_info in list_of_block_of_vlan_database
    ]

    vlan_db_facts = []
    for vlan_info in vlan_db_facts_intermediate:
        if len(vlan_info["vlan_ids"]) > 1:
            vlan_db_facts = vlan_db_facts + [
                {"vlan_id": vlan_id} for vlan_id in vlan_info["vlan_ids"]
            ]

        # sloppy below
        vlan_info["vlan_id"] = vlan_info["vlan_ids"][0]
        del vlan_info["vlan_ids"]
        vlan_db_facts.append(vlan_info)

    final_vlan_db_facts = []

    temp_dict = {}
    for row in vlan_db_facts:
        #logging.error(row)
        if row["vlan_id"] in temp_dict:
            temp_dict[row["vlan_id"]].update(row)
        else:
            temp_dict[row["vlan_id"]] = row

    for row in vlan_interface_facts:
        #logging.error(row)
        if row["vlan_id"] in temp_dict:
            temp_dict[row["vlan_id"]].update(row)
        else:
            temp_dict[row["vlan_id"]] = row


    list_of_phy_log_interfaces = re.findall(
        r"(^interface [^V].*(\n[^\n]+)*\n)", text_body, re.MULTILINE
    )


    phy_log_interface_facts = [  # list comprehension
        {
            "intr_id": str(re.search(r"\w+[\d/\.]+", interface[0].splitlines()[0]).group()),
            "intr_name": re.search(r"description (.+)", interface[0])
            and re.search(r"description (.+)", interface[0]).group(1),
            "ipv4": re.findall(r"ip address (.+)", interface[0]),
            "ipv6": re.findall(r"ipv6 address (.+)", interface[0]),
        }
        for interface in list_of_phy_log_interfaces
    ]

    phy_log_interface_facts_if_ips = [
        x for x in phy_log_interface_facts if x["ipv4"] or x["ipv6"]
    ]


    for row in phy_log_interface_facts_if_ips:
        #logging.error(row)
        if row["intr_id"] in temp_dict:
            temp_dict[row["intr_id"]].update(row)
        else:
            temp_dict[row["intr_id"]] = row

    return temp_dict



fake_file = io.StringIO()


file_dir = str(input("Please input the absolute path or relative path of the folder where all the config files are stored:"))
all_files = os.listdir(file_dir)
output_csv = str(input("Please input the output csv file name(recommended format:date_site_type):"))
with open(output_csv, "w") as ivc:
    headers = [
        "vlan_id",
        "intr_id",
        "vlan_db_name",
        "vlan_intr_name",
        "intr_name",
        "ipv4.1",
        "ipv4.2",
        "ipv4.3",
        "ipv6.1",
        "ipv6.2",
        "ipv6.3",
        "Hostname"
    ]

    csv_writer = csv.DictWriter(ivc, fieldnames=headers)
    csv_writer.writeheader()

    for conf_file in all_files:
        with open(file_dir + "/" + conf_file, "r") as f:
            config = f.read()
            temp_dict = parseNexusConf(config)

            for row in temp_dict.values():
                row["ipv4.1"] = (
                    row.get("ipv4") is not None and len(row["ipv4"]) > 0 and row["ipv4"][0]
                )
                row["ipv4.2"] = (
                    row.get("ipv4") is not None and len(row["ipv4"]) > 1 and row["ipv4"][1]
                )
                row["ipv4.3"] = (
                    row.get("ipv4") is not None and len(row["ipv4"]) > 2 and row["ipv4"][2]
                )
                row["ipv6.1"] = (
                    row.get("ipv6") is not None and len(row["ipv6"]) > 0 and row["ipv6"][0]
                )
                row["ipv6.2"] = (
                    row.get("ipv6") is not None and len(row["ipv6"]) > 1 and row["ipv6"][1]
                )
                row["ipv6.3"] = (
                    row.get("ipv6") is not None and len(row["ipv6"]) > 2 and row["ipv6"][2]
                )
                if row.get("ipv4") is not None:
                    del row["ipv4"]
                if row.get("ipv6") is not None:
                    del row["ipv6"]
                row["Hostname"] = conf_file
                csv_writer.writerow(row)