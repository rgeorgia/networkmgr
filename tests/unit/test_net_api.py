import pytest
from pathlib import Path
import site
from subprocess import Popen, PIPE

site.addsitedir(str(Path(__file__).absolute().parent.parent.parent.joinpath('src')))
import net_api
from net_api import RcType


class MockPopen(object):
    def __init__(self, args, shell=True, stdout=PIPE, universal_newlines=True):
        self.args = args
        self.stdout = stdout
        self.shell = shell
        self.universal_newlines = universal_newlines

    @staticmethod
    def communicate():
        return "", None


def test_rc_type_class_is_rc():
    rc_type = RcType()
    assert rc_type.rc == 'rc-'
    assert rc_type.network_service == 'network'
    assert rc_type.is_openrc


def test_rc_type_class_not_rc(monkeypatch):
    monkeypatch.setattr(net_api, "Popen", MockPopen)
    rc_type = RcType()

    assert rc_type.rc == ''
    assert rc_type.network_service == 'netif'
    assert rc_type.is_openrc is False


def test_network_device_list_is_list():
    assert isinstance(net_api.network_device_list(), list)


def test_network_device_list_no_loopback():
    assert 'lo' not in net_api.network_device_list()


def test_openrc():
    assert net_api.openrc


# TODO: create fake rc.conf file to simulate missing card
def test_is_wifi_card_added():
    assert net_api.is_wifi_card_added()

def test_read_rc_conf():
    result = net_api.read_rc_conf()
    print(f"\n====== {result} =====\n")