#!/usr/bin/env python
import fileinput
import os
import socket
import platform
from freebsd_sysctl import Sysctl

"""
config_card:
    1. Check if user is root, if not alert and exit
    1a. Assumes GhostBSD or FreeBSD
    2. get a list of all the cards / network devices recognized by the system
    3. see if a wifi device has been recognized by the system
    4. read /etc/rc.conf file
    5. Check to see if system is openrc or rc.d
    6. Be able to restart network if needed
    7. Check if network device is already in /etc/rc.conf file. If network device is not in rc.conf
       file add it. 
       NOTE: FreeBSD is ifconfig_nic_enable
"""

not_valid_if = {
    'lo': 'loopback',
    'fwe': 'firewire',
    'fwip': 'IP over FireWire',
    'tap': 'tuntap tunnel',
    'plip': 'printer port Internet Protocol driver',
    'pfsync': 'packet filter state table sychronisation interface',
    'pflog': 'packet filter logging interface',
    'tun': 'tunnel software network interface',
    'sl': '',
    'faith': 'IPv6-to-IPv4 TCP relay capturing interface',
    'ppp': 'Point to Point Protocol',
    'bridge': 'if_bridge – network bridge device',
    'ixautomation': 'testing framework for iX projects',
    'vm-ixautomation': 'testing framework for iX projects',
    'wg': 'Wire Guard',
}


def i_am_root() -> bool:
    return os.geteuid() == 0


class ConfigCardException(Exception):
    pass


class RcConfig:
    def __init__(self):
        self._flags_types = None
        self.rc_conf_file = '/etc/rc.conf'
        self._wifi_card = Sysctl("net.wlan.devices").value

    @property
    def enabling_value(self):
        return ["YES", "TRUE", "ON", "1", "NO", "FALSE", "OFF", "0"]

    @property
    def wifi_card(self):
        return self._wifi_card

    def read_rc_conf(self):
        try:
            with open(self.rc_conf_file) as f_name:
                data = f_name.readlines()
        except FileNotFoundError as e:
            raise ConfigCardException(f"{self.__class__.__name__} : {e}")
        return data

    def replace_line(self, to_replace: str, replacement: str):
        with fileinput.input(files=self.rc_conf_file, inplace=True, backup=".bak") as f:
            for line in f:
                if to_replace in line:
                    print(replacement.strip())
                else:
                    print(line.strip())

    def add_line(self, rc_string: str):
        with open(self.rc_conf_file, "a") as f:
            f.write(f"{rc_string}\n")


class FreeBSDRc(RcConfig):
    def __init__(self):
        super().__init__()


class AutoConfigure:
    def __init__(self):
        self.os = platform.system()


    @property
    def nic_cards(self):
        return [item[1] for item in socket.if_nameindex() if 'lo' not in item[1]]


AutoConfigure()
if i_am_root():
    AutoConfigure()
else:
    print(f"Looks like you do not have sufficient privs to run {os.path.basename(__file__)}. "
          f"Try using sudo {os.path.basename(__file__)}")
