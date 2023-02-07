import re
import json
import ipaddress
import datetime 


def define_ports(line):
    port = ""
    # set logical-systems <LOGICAL_SYSTEM_NAME> applications application Port-23456-23457 protocol tcp
    port_name = line.split()[5]
    if "-" in port_name:
        port_low = port_name.split("-")[1]
        try:
            # Port-23456-23457
            port_high = port_name.split("-")[2]
        except:
            port_high = port_name.split("-")[1]
        if port_low == port_high:
            port = port_low
        else:
            port = f"{port_low}-{port_high}"
        return port


def define_addr(line, description):
    address_name = line.split()[7]
    subnet = line.split()[8]
    converted_file.write(f"edit {address_name}\n")
    converted_file.write(f"set subnet {subnet}\n")
    converted_file.write(f"set comment {description}\n")
    converted_file.write("next\n")


def define_addrgrp(line):
    grp_name = line.split()[7]
    address_name = line.split()[9]
    converted_grp.write(f"edit {grp_name}\n")
    converted_grp.write(f"append member {address_name}\n")
    converted_grp.write("next\n")

# Need to define interface for vlan 
def define_vlans(line):
    vlan_id = line.split()[6]
    vlan_name = line.split()[10]
    vlan_name = ipaddress.ip_interface(vlan_name)
    vlan_name_new = vlan_name.network
    vlan_ip = line.split()[10]
    converted_vlans.write(f"edit {vlan_name_new}\n")
    converted_vlans.write("set vdom 'BMC'\n")
    converted_vlans.write(f"set ip {vlan_ip}\n")
    converted_vlans.write("""set allowaccess ping\nset status down\nset role dmz\nset interface 'PO17'\n""")
    converted_vlans.write(f"set vlanid {vlan_id}\n")
    converted_vlans.write("next\n")


with open("SRX_to_Forti\\backup_j.txt") as srx_backup,\
        open("SRX_to_Forti\policies_j.json") as policies_j,\
        open("SRX_to_Forti\schedules.json") as schedules_j,\
        open("SRX_to_Forti\converted.txt", "w") as converted_file,\
        open("SRX_to_Forti\converted_grp.txt", "w") as converted_grp,\
        open("SRX_to_Forti\converted_ports.txt", "w") as converted_ports,\
        open("SRX_to_Forti\\vlans.txt", "w") as converted_vlans,\
        open("SRX_to_Forti\converted_policies.txt", "w") as converted_policies,\
        open("SRX_to_Forti\converted_schedules.txt", "w") as converted_schedules:
    save_desc = ""
    policy = {}
    for line in srx_backup.readlines():
        if "protocol tcp" in line:
            port_name = define_ports(line)
            if port_name:
                converted_ports.write(f"edit Port-{port_name}\n")
                converted_ports.write(f"set tcp-portrange {port_name}\n")
                converted_ports.write("next\n")
        elif "protocol udp" in line:
            port_name = define_ports(line)
            if port_name:
                converted_ports.write(f"edit Port-{port_name}\n")
                converted_ports.write(f"set udp-portrange {port_name}\n")
                converted_ports.write("next\n")
        elif re.search("address-book.*address.*description", line):
            save_desc = line.split()[9]
        # ?!.* for exclude address-sets
        elif re.search("address-book.*address(?!.*description)", line) and\
                re.search("address-book(?!.*address-set).*address", line):
            define_addr(line, save_desc)
            save_desc = "''"
        elif re.search("address-book.*address-set(?!.*Grp-BlockIP).*address", line):
            define_addrgrp(line)
        elif re.search("interfaces reth\d unit.*family inet", line):
            define_vlans(line)


    js_schedules_j = json.load(schedules_j)
    for item in js_schedules_j["configuration"]["logical-systems"][0]["schedulers"]["scheduler"]:
        sch_name = item["name"]
        converted_schedules.write(f"edit {sch_name}\n")
        print(sch_name)
        try:
            if item["start-date"][-1]["start-date"]:
                sch_start = item["start-date"][-1]["start-date"]
                sch_start_time = sch_start.split(".")[1]
                sch_start_date = sch_start.split(".")[0]
                sch_start_date_new = datetime.datetime.strptime(sch_start_date,'%Y-%m-%d').strftime('%Y/%m/%d')
                converted_schedules.write(f"set start {sch_start_time} {sch_start_date_new}\n")
                print(f"start date : {sch_start}")
            if item["start-date"][-1]["stop-date"]:
                sch_stop = item["start-date"][-1]["stop-date"]
                sch_stop_time = sch_stop.split(".")[1]
                sch_stop_date = sch_stop.split(".")[0]
                sch_stop_date_new = datetime.datetime.strptime(sch_stop_date,'%Y-%m-%d').strftime('%Y/%m/%d')
                converted_schedules.write(f"set end {sch_stop_time} {sch_stop_date_new}\n")
                print(f"stop date :{sch_stop}")
            # if item["daily"]:
            #     print(item["daily"])
        except (Exception) as error:
            print(error)
        converted_schedules.write("next\n")


    js_policies_j = json.load(policies_j)
    policy_id = 2
    for line in js_policies_j["configuration"]["logical-systems"][0]["security"]["policies"]["policy"]:
        src_int = line["from-zone-name"]
        dst_int = line["to-zone-name"]
        count = 0
        for i in line["policy"]:
            policy_name = line["policy"][count]["name"]
            #print(policy_name)
            src_addr_lst = line["policy"][count]["match"]["source-address"]
            if src_addr_lst[0] == "any":
                src_addr = "all"
            else:
                src_addr = ' '.join(src_addr_lst)
            dst_addr_lst = line["policy"][count]["match"]["destination-address"]
            if dst_addr_lst[0] == "any":
                dst_addr = "all"
            else:
                dst_addr = ' '.join(dst_addr_lst)
            port_lst = line["policy"][count]["match"]["application"]
            #Lambda worked fine but we dont want junos-icmp-pin >>> icmp-ping ... we want this: PING
            #port_lst = list(map(lambda st : str.replace(st, 'junos-', ''),port_lst))
            #Convert a list to a space-separated string in Python with join method
            if port_lst[0] == "any":
                port = "ALL"
            else:
                port = ' '.join(port_lst)
            thendic = line["policy"][count]["then"]
            thenkey , thenval = list(thendic.items())[0]
            action = thenkey
            if action == "permit":
                action = "accept"
            converted_policies.write(f"edit {policy_id}\n")
            converted_policies.write(f"set name {policy_name}-P{policy_id}\n")
            converted_policies.write(f"set srcintf {src_int}\n")
            converted_policies.write(f"set dstintf {dst_int}\n")
            converted_policies.write(f"set srcaddr {src_addr}\n")
            converted_policies.write(f"set dstaddr {dst_addr}\n")
            converted_policies.write(f"set action {action}\n")
            if "scheduler-name" in line["policy"][count]:
                    scheduler_name = line["policy"][count]["scheduler-name"]
                    converted_policies.write(f"set schedule {scheduler_name}\n")
                    print(scheduler_name)
            else:
                converted_policies.write("set schedule always\n")
                pass
            converted_policies.write(f"set service {port}\n")
            #list(filter(lambda item: converted_policies.write(f"set service {item}\n"), port))
            #converted_policies.write(f"set service {port}\n")
            if action == "accept":
                converted_policies.write(f"set utm-status enable\nset ssl-ssh-profile 'certificate-inspection'\nset ips-sensor 'BMC_High'\nset logtraffic all\nnext\n")
            else:
                converted_policies.write(f"set logtraffic all\nnext\n")
            count+=1
            policy_id +=1

        
