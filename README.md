# Juniper SRX (Junos OS) to FortiGate Configuration Converter



This is a Python script that converts Juniper SRX firewall configuration to FortiGate firewall configuration. The script supports conversion of the following configurations:

**Policies**

**Schedulers (onetime Schedulers)** 

**Addresses**

**Address groups**

**Services (custom ports)**

**VLANs (It currently works for one specific interface)**



## Getting Started


These instructions will get you a copy of the project up and running on your local machine for conversion process.


## Prerequisites


you need to take a full backup of the configuration in the "display set" mode for addresses , address groups and services with the file name: backup_j.txt

**Command : show configuration | display set**
 

You also needed to take a custom configuration for schedulers and policies with the file names : schedules.json , policies_j.json

**Command : show configuration logical-systems <LOGICAL_SYSTEM_NAME> security policies | display json**


## Usage


The script will require the path to the **Juniper SRX** configuration files in **txt** and **JSON** format.

backup_j.txt

schedules.json

policies_j.json

The script will start the conversion process and will generate the output files in the same directory as the script.

**After the conversion process is finished, you need to manually make changes to juniper's default ports,**

for example in converted_policies.txt find junos-ping and edit it with PING.


## Contributing

These are the items I am working on:
- Recurring schedulers
- Juniper SRX default ports


