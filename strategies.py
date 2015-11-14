#!/usr/bin/env python
"""Classes for application instances distribution within infrastructure
"""
import json
from thread import start_new_thread

from minstore.constants import *
from minstore.helpers import Helpers


class Spread(object):
    """Class for mirroring and bridging strategies
    """

    def __init__(self, config_path, route=''):
        """Constructor
        """
        self._config_path = config_path
        self._route = route
        self._servers = list()

        self._load_servers()

    def _load_servers(self):
        with open(self._config_path, 'rb') as config_file:
            content = config_file.read()
            self._servers = content.split()

    def _read_bridge_enabled(self):
        """
        Checks the bridge mode in servers list.
        :return: bool
        """
        if self._servers and self._servers[0] == '*':
            self._servers.pop(0)
            return True

        else:
            return False

    def spread_put(self, record):
        """
        Spreads a put call in the background
        :param record: dict
        """
        bridge_mode = self._read_bridge_enabled()
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            self._async_put(url, record['uid'], record, bridge_mode=bridge_mode)

    def spread_delete(self, uid):
        """
        Spreads a delete call in the background
        :param uid: str
        """
        bridge_mode = self._read_bridge_enabled()
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            self._async_delete(url, uid, bridge_mode=bridge_mode)

    @classmethod
    def _put_job(cls, url, dirs, params, data):
        Helpers.request_put(url=url, dirs=dirs, data=data, params=params)

    def _async_put(self, url, uid, record, bridge_mode):
        content = json.dumps(record)

        data = {'value': content}
        params = {MIRROR_MODE: True}

        if bridge_mode:
            params[BRIDGE_MODE] = True

        start_new_thread(self._put_job, (url, [uid], params, data))

    @classmethod
    def _delete_job(cls, url, dirs, params):
        Helpers.request_delete(url=url, dirs=dirs, params=params)

    def _async_delete(self, url, uid, bridge_mode):
        params = {MIRROR_MODE: True}

        if bridge_mode:
            params[BRIDGE_MODE] = True

        start_new_thread(self._delete_job, (url, [uid], params))