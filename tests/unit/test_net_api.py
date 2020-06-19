import pytest
from pathlib import Path
import site
from subprocess import Popen, PIPE

site.addsitedir(str(Path(__file__).absolute().parent.parent.parent.joinpath('src')))
import net_api as net_api


class MockPopen(object):
    def __init__(self, args, shell=True, stdout=PIPE, universal_newlines=True):
        self.args = args
        self.stdout = stdout
        self.shell = shell
        self.universal_newlines = universal_newlines

    @staticmethod
    def communicate():
        return "", None


def test_is_openrc():
    assert net_api.is_openrc()


def test_not_openrc(monkeypatch):
    monkeypatch.setattr(net_api.RcType, "Popen", MockPopen)
    result = net_api.is_openrc()
    assert result is False


def test_rc_type_class_is_rc():
    assert net_api.RcType().rc == 'rc-'
    assert net_api.RcType().network_service == 'network'


def test_rc_type_class_not_rc(monkeypatch):
    monkeypatch.setattr(net_api, "Popen", MockPopen)
    assert net_api.RcType().rc == ''
    assert net_api.RcType().network_service == 'netif'
