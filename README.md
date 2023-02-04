Juniper SRX to FortiGate Configuration Converter

This is a Python script that converts Juniper SRX firewall configuration to FortiGate firewall configuration. The script supports conversion of the following configurations:

Addresses
Address groups
Services
Schedulers
Policies
Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

Prerequisites
You need to have Python 3 installed on your system. You can download the latest version of Python from the official website here.

Installation
Clone the repository to your local machine using the following command:
bash
Copy code
git clone https://github.com/YOUR_GITHUB_USERNAME/juniper-srx-to-fortigate-converter.git
Navigate to the cloned repository:
bash
Copy code
cd juniper-srx-to-fortigate-converter
Run the script:
Copy code
python3 convert.py
Usage

The script will prompt you to enter the path to the Juniper SRX configuration file. After entering the path, the script will start the conversion process and will generate the output file in the same directory as the script with the name output.conf.

Contributing

Feel free to submit pull requests and bug reports. For major changes, please open an issue first to discuss what you would like to change.

License

This project is licensed under the MIT License - see the LICENSE file for details.