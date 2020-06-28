from subprocess import PIPE

import pytest


class MockPopen(object):
    def __init__(self, args, shell=True, stdout=PIPE, universal_newlines=True):
        self.args = args
        self.stdout = stdout
        self.shell = shell
        self.universal_newlines = universal_newlines
        self._expected = ''

    @property
    def expected(self):
        return self._expected

    @expected.setter
    def expected(self, request):
        self._expected = request

    def communicate(self):
        return self.expected, None

    def readlines(self):
        return self.expected


@pytest.fixture()
def mock_popen():
    def _communicate(request):
        mp = MockPopen
        mp.expected = request
        return mp

    return _communicate


class MockSysctl(object):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def value():
        return ""

    @staticmethod
    def if_nameindex():
        return [(1, 'em3'), (2, 'em5'), (3, 'lo0'), (4, 'wlan2'), ]


@pytest.fixture()
def mock_sysctl():
    return MockSysctl
