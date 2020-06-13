#!/usr/bin/env python
import os
import socket
import platform

"""
config_card:
    1. Check if user is root, if not alert and exit
    1a. Check what BSD you are running on.
    2. get a list of all the cards / network devices recognized by the system
    3. see if a wifi device has been recognized by the system
    4. read /etc/rc.conf file
    5. Check to see if system is openrc or rc.d
    6. Be able to restart network if needed
    7. Check if network device is already in /etc/rc.conf file. If network device is not in rc.conf
       file add it. 
       NOTE: FreeBSD is ifconfig_nic_enable
       NetBSD uses /etc/ifconfig.netif and dhcpcd_flags="-qM nic0 nic1"
    
"""

not_valid_if = [
    "lo",
    "fwe",
    "fwip",
    "tap",
    "plip",
    "pfsync",
    "pflog",
    "tun",
    "sl",
    "faith",
    "ppp",
    "brige",
    "ixautomation",
    "vm-ixautomation",
    "wg"
]


def i_am_root() -> bool:
    return os.geteuid() == 0


class AutoConfigure:
    def __init__(self):
        self.os = platform.system()

    @property
    def nic_cards(self):
        return [item[1] for item in socket.if_nameindex() if 'lo' not in item[1]]

    @staticmethod
    def read_rc_conf(self):
        rc_conf_file = '/etc/rc.conf'
        with open(rc_conf_file, 'r') as rcf:
            rc_data = rcf.readlines()


if i_am_root():
    AutoConfigure()
else:
    print(f"Looks like you do not have sufficient privs to run {os.path.basename(__file__)}. "
          f"Try using sudo {os.path.basename(__file__)}")
