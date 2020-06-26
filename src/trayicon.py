#!/usr/bin/env python3

import gi
from gi.repository import Gtk, GObject, GLib
from time import sleep
import threading
import locale
import os
from .net_api import stopnetworkcard, is_a_new_network_card_install
from .net_api import startnetworkcard, wifi_disconnection
from .net_api import stop_all_network, start_all_network, connect_to_ssid
from .net_api import disable_wifi, enable_wifi
from .net_api import connection_status, network_dictionary, openrc
from .authentication import Authentication, OpenWpaSupplicant

gi.require_version('Gtk', '3.0')

encoding = locale.getpreferredencoding()
threadBreak = False
GObject.threads_init()
wpa_supplican = "/etc/wpa_supplicant.conf"


class TrayIcon(object):

    def __init__(self):
        self.menu = Gtk.Menu()
        self.cardinfo = network_dictionary()
        self.thr = threading.Thread(target=self.updatetrayloop)
        self.ifruning = False
        self.statusIcon = Gtk.StatusIcon()
        self.statusIcon.set_visible(True)
        self.statusIcon.connect("activate", self.left_click)
        self.statusIcon.connect('popup-menu', self.icon_clicked)

    @staticmethod
    def stop_manager():
        Gtk.main_quit()

    def left_click(self, status_icon):
        if not self.thr.is_alive():
            self.thr.start()
        button = 1
        time = Gtk.get_current_event_time()
        position = Gtk.StatusIcon.position_menu
        self.nm_menu().popup(None, None, position, status_icon, button, time)

    def icon_clicked(self, status_icon, button, time):
        if not self.thr.is_alive():
            self.thr.start()
        position = Gtk.StatusIcon.position_menu
        self.nm_menu().popup(None, None, position, status_icon, button, time)

    def nm_menu(self):
        e_title = Gtk.MenuItem()
        e_title.set_label("Ethernet Network")
        e_title.set_sensitive(False)
        self.menu.append(e_title)
        self.menu.append(Gtk.SeparatorMenuItem())
        cardnum = 1
        wifinum = 1
        cards = self.cardinfo['cards']
        for netcard in cards:
            connection_state = cards[netcard]['state']["connection"]
            if "wlan" not in netcard:
                if connection_state == "Connected":
                    wired_item = Gtk.MenuItem("Wired %s Connected" % cardnum)
                    wired_item.set_sensitive(False)
                    self.menu.append(wired_item)
                    disconnect_item = Gtk.ImageMenuItem("Disable")
                    disconnect_item.connect("activate", self.disconnectcard,
                                            netcard)
                    self.menu.append(disconnect_item)
                elif connection_state == "Disconnected":
                    notonline = Gtk.MenuItem("Wired %s Disconnected" % cardnum)
                    notonline.set_sensitive(False)
                    self.menu.append(notonline)
                    wired_item = Gtk.MenuItem("Enable")
                    wired_item.connect("activate", self.connectcard, netcard)
                    self.menu.append(wired_item)
                else:
                    disconnected = Gtk.MenuItem("Wired %s Unplug" % cardnum)
                    disconnected.set_sensitive(False)
                    self.menu.append(disconnected)
                    cardnum += 1
                self.menu.append(Gtk.SeparatorMenuItem())
            elif "wlan" in netcard:
                if connection_state == "Disabled":
                    wd_title = Gtk.MenuItem()
                    wd_title.set_label("WiFi %s Disabled" % wifinum)
                    wd_title.set_sensitive(False)
                    self.menu.append(wd_title)
                    enawifi = Gtk.MenuItem("Enable Wifi %s" % wifinum)
                    enawifi.connect("activate", self.enable_wifi, netcard)
                    self.menu.append(enawifi)
                elif connection_state == "Disconnected":
                    d_title = Gtk.MenuItem()
                    d_title.set_label("WiFi %s Disconnected" % wifinum)
                    d_title.set_sensitive(False)
                    self.menu.append(d_title)
                    self.wifi_list_menu(netcard, None, False, cards)
                    diswifi = Gtk.MenuItem("Disable Wifi %s" % wifinum)
                    diswifi.connect("activate", self.disable_wifi, netcard)
                    self.menu.append(diswifi)
                else:
                    ssid = cards[netcard]['state']["ssid"]
                    bssid = cards[netcard]['state']["bssid"]
                    bar = cards[netcard]['info'][bssid][4]
                    wc_title = Gtk.MenuItem("WiFi %s Connected" % wifinum)
                    wc_title.set_sensitive(False)
                    self.menu.append(wc_title)
                    connection_item = Gtk.ImageMenuItem(ssid)
                    connection_item.set_image(self.openwifi(bar))
                    connection_item.show()
                    disconnect_item = Gtk.MenuItem("Disconnect from %s" % ssid)
                    disconnect_item.connect("activate", self.disconnectwifi,
                                            netcard)
                    self.menu.append(connection_item)
                    self.menu.append(disconnect_item)
                    self.wifi_list_menu(netcard, bssid, True, cards)
                    diswifi = Gtk.MenuItem("Disable Wifi %s" % wifinum)
                    diswifi.connect("activate", self.disable_wifi, netcard)
                    self.menu.append(diswifi)
                self.menu.append(Gtk.SeparatorMenuItem())
                wifinum += 1

        if openrc is True:
            if self.cardinfo['service'] is False:
                open_item = Gtk.MenuItem("Enable Networking")
                open_item.connect("activate", self.open_network)
                self.menu.append(open_item)
            else:
                close_item = Gtk.MenuItem("Disable Networking")
                close_item.connect("activate", self.close_network)
                self.menu.append(close_item)
        else:
            print('service netif status not supported')
        close_manager = Gtk.MenuItem("Close Network Manager")
        close_manager.connect("activate", self.stop_manager)
        self.menu.append(close_manager)
        self.menu.show_all()
        return self.menu

    def wifi_list_menu(self, wificard, cbssid, passes, cards):
        wiconncmenu = Gtk.Menu()
        avconnmenu = Gtk.MenuItem("Available Connections")
        avconnmenu.set_submenu(wiconncmenu)
        for bssid in cards[wificard]['info']:
            ssid = cards[wificard]['info'][bssid][0]
            sn = cards[wificard]['info'][bssid][4]
            caps = cards[wificard]['info'][bssid][6]
            if passes is True:
                if cbssid != bssid:
                    menu_item = Gtk.ImageMenuItem(ssid)
                    if caps == 'E' or caps == 'ES':
                        menu_item.set_image(self.openwifi(sn))
                        menu_item.connect("activate", self.menu_click_open,
                                          ssid, bssid, wificard)
                    else:
                        menu_item.set_image(self.securewifi(sn))
                        menu_item.connect("activate", self.menu_click_lock,
                                          ssid, bssid, wificard)
                    menu_item.show()
                    wiconncmenu.append(menu_item)
            else:
                menu_item = Gtk.ImageMenuItem(ssid)
                if caps == 'E' or caps == 'ES':
                    menu_item.set_image(self.openwifi(sn))
                    menu_item.connect("activate", self.menu_click_open, ssid,
                                      bssid, wificard)
                else:
                    menu_item.set_image(self.securewifi(sn))
                    menu_item.connect("activate", self.menu_click_lock, ssid,
                                      bssid, wificard)
                menu_item.show()
                wiconncmenu.append(menu_item)
        self.menu.append(avconnmenu)

    def menu_click_open(self, ssid, bssid, wificard):
        if bssid in open(wpa_supplican).read():
            connect_to_ssid(ssid, wificard)
        else:
            OpenWpaSupplicant(ssid, bssid, wificard)
        self.updateinfo()
        self.ifruning = False

    def menu_click_lock(self, ssid, bssid, wificard):
        if bssid in open(wpa_supplican).read():
            connect_to_ssid(ssid, wificard)
        else:
            Authentication(ssid, bssid, wificard)
        self.updateinfo()
        self.ifruning = False

    def disconnectwifi(self, wificard):
        wifi_disconnection(wificard)
        self.updateinfo()
        self.ifruning = False

    def disable_wifi(self, wificard):
        disable_wifi(wificard)
        self.updateinfo()
        self.ifruning = False

    def enable_wifi(self, wificard):
        enable_wifi(wificard)
        self.updateinfo()
        self.ifruning = False

    def connectcard(self, netcard):
        startnetworkcard(netcard)
        self.updateinfo()
        self.ifruning = False

    def disconnectcard(self, netcard):
        stopnetworkcard(netcard)
        self.updateinfo()
        self.ifruning = False

    def close_network(self, ):
        stop_all_network()
        self.updateinfo()
        self.ifruning = False

    def open_network(self, ):
        start_all_network()
        self.updateinfo()
        self.ifruning = False

    @staticmethod
    def openwifi(bar):
        img = Gtk.Image()
        if bar > 75:
            img.set_from_icon_name("nm-signal-100", Gtk.IconSize.MENU)
        elif bar > 50:
            img.set_from_icon_name("nm-signal-75", Gtk.IconSize.MENU)
        elif bar > 25:
            img.set_from_icon_name("nm-signal-50", Gtk.IconSize.MENU)
        elif bar > 5:
            img.set_from_icon_name("nm-signal-25", Gtk.IconSize.MENU)
        else:
            img.set_from_icon_name("nm-signal-00", Gtk.IconSize.MENU)
        img.show()
        return img

    @staticmethod
    def securewifi(bar):
        img = Gtk.Image()
        if bar > 75:
            img.set_from_icon_name("nm-signal-100-secure", Gtk.IconSize.MENU)
        elif bar > 50:
            img.set_from_icon_name("nm-signal-75-secure", Gtk.IconSize.MENU)
        elif bar > 25:
            img.set_from_icon_name("nm-signal-50-secure", Gtk.IconSize.MENU)
        elif bar > 5:
            img.set_from_icon_name("nm-signal-25-secure", Gtk.IconSize.MENU)
        else:
            img.set_from_icon_name("nm-signal-00-secure", Gtk.IconSize.MENU)
        img.show()
        return img

    def updateinfo(self):
        if self.ifruning is False:
            self.ifruning = True
            defaultcard = self.cardinfo['default']
            default_type = self.network_type(defaultcard)
            sleep(1)
            GLib.idle_add(self.updatetray, defaultcard, default_type)

    def updatetray(self, defaultdev, default_type):
        self.updatetrayicon(defaultdev, default_type)
        self.tray_status(defaultdev)

    def updatetrayloop(self):
        while True:
            self.checkfornewcard()
            self.updateinfo()
            self.ifruning = False
            sleep(20)

    @staticmethod
    def network_type(defaultdev):
        if defaultdev is None:
            return None
        elif 'wlan' in defaultdev:
            return 'wifi'
        else:
            return 'wire'

    def default_wifi_state(self, defaultdev):
        info = self.cardinfo['cards'][defaultdev]
        if info['state']["connection"] == "Connected":
            bssid = info['state']["bssid"]
            return info['info'][bssid][4]
        else:
            return None

    @staticmethod
    def checkfornewcard():
        if os.path.exists("/usr/local/bin/netcardmgr"):
            if is_a_new_network_card_install() is True:
                os.system("netcardmgr")

    def updatetrayicon(self, defaultdev, card_type):
        if card_type is None:
            self.statusIcon.set_from_icon_name('nm-no-connection')
        elif card_type == 'wire':
            self.statusIcon.set_from_icon_name('nm-adhoc')
        else:
            wifi_state = self.default_wifi_state(defaultdev)
            if wifi_state is None:
                self.statusIcon.set_from_icon_name('nm-no-connection')
            elif wifi_state > 80:
                self.statusIcon.set_from_icon_name('nm-signal-100')
            elif wifi_state > 60:
                self.statusIcon.set_from_icon_name('nm-signal-75')
            elif wifi_state > 40:
                self.statusIcon.set_from_icon_name('nm-signal-50')
            elif wifi_state > 20:
                self.statusIcon.set_from_icon_name('nm-signal-25')
            else:
                self.statusIcon.set_from_icon_name('nm-signal-00')

    def tray_status(self, defaultdev):
        self.statusIcon.set_tooltip_text("%s" % connection_status(defaultdev))

    def tray(self):
        self.ifruning = False
        self.thr.setDaemon(True)
        self.thr.start()
        Gtk.main()
