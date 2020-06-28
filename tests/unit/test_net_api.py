import pytest
from pathlib import Path
import site

site.addsitedir(str(Path(__file__).absolute().parent.parent.parent.joinpath('src')))
import net_api


def test_rc_type_class_is_rc():
    rc_type = net_api.RcType()
    assert rc_type.rc == 'rc-'
    assert rc_type.network_service == 'network'
    assert rc_type.is_openrc


def test_rc_type_class_not_rc(monkeypatch, mock_popen):
    monkeypatch.setattr(net_api, "Popen", mock_popen(''))
    rc_type = net_api.RcType()

    assert rc_type.rc == ''
    assert rc_type.network_service == 'netif'
    assert rc_type.is_openrc is False


def test_network_device_list_no_loopback():
    assert 'lo' not in net_api.network_device_list()


def test_openrc():
    assert net_api.openrc


def test_read_rc_conf():
    result = net_api.read_rc_conf()
    assert isinstance(result, str)


def test_read_rc_conf_error():
    with pytest.raises(SystemExit) as bad_rc_conf:
        net_api.read_rc_conf('/etc/rc.con')
    assert bad_rc_conf.type == SystemExit
    assert bad_rc_conf.value.code == 1


wifi_params = [('wlan0', 'c4:41:1e:40:68:d0', 'c4:41:1e:40:68:d0'), ('wlan99', 'c4:41:1e:40:68:d0', ''),
               ('wlan0', 'c4:41:1e:40:68', 'c4:41:1e:40:68:d0'), ('wlan0', 'c4:41:1e:40:68:d1', '')]
wifi_params_id = [f'Card: {item[0]}, BSSID: {item[1]}' for item in wifi_params]


@pytest.mark.parametrize('wificard, bssid, expected', wifi_params, ids=wifi_params_id)
def test_scan_wifi_bssid(wificard, bssid, expected):
    result = net_api.scan_wifi_bssid(wificard=wificard, bssid=bssid)
    assert isinstance(result, str)
    assert expected in result


def test_network_device_list_is_list():
    assert isinstance(net_api.network_device_list(), list)


def test_is_wifi_card_added():
    assert net_api.is_wifi_card_added()


def test_is_wifi_card_added_not_in_list(monkeypatch, mock_sysctl):
    monkeypatch.setattr(net_api, "socket", mock_sysctl)
    assert net_api.is_wifi_card_added()


def test_is_wifi_card_added_not_in_rc_conf(monkeypatch, mock_sysctl):
    monkeypatch.setattr(net_api, 'Sysctl', mock_sysctl)
    assert not net_api.is_wifi_card_added()


# def test_if_wired_card_added_patched(monkeypatch):
#     class MockSocket(object):
#         def __init__(self, args):
#             self.args = args
#
#         @staticmethod
#         def if_nameindex():
#             return [(1, 'em3'), (2, 'em5'), (3, 'lo0'), (4, 'wlan2'), ]
#
#     monkeypatch.setattr(net_api, "socket", MockSocket)
#     assert net_api.if_wired_card_added()
#
#
# def test_if_wired_card_added():
#     assert not net_api.if_wired_card_added()


def test_is_a_new_network_card_install():
    assert net_api.is_a_new_network_card_install()


# TODO: need to work on this test, it assumes cards have been discovered.
def test_if_card_is_online():
    for card in net_api.network_device_list():
        assert net_api.if_card_is_online(card)


def test_if_card_is_online_not_online(monkeypatch, mock_popen):
    monkeypatch.setattr(net_api, "Popen", mock_popen('inet'))
    assert not net_api.if_card_is_online('em11')


def test_default_card(monkeypatch, mock_popen):
    monkeypatch.setattr(net_api, "Popen", mock_popen(['default            192.168.1.1        UGS         em0']))
    result = net_api.default_card()
    print(f"\n======= {result} =======\n")
    assert False


def test_default_card_is_str():
    assert isinstance(net_api.default_card(), str)
