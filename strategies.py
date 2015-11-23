#!/usr/bin/env python
"""Classes for application instances distribution within infrastructure
"""
from Queue import Queue
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
        self._cache = None
        self._request_bridge = None
        self._cache_inputs = Queue()

        self._load_servers()
        self._set_bridge_request()

    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, instance):
        self._cache = instance

    def _set_bridge_request(self):
        if self._request_bridge is None:
            self._request_bridge = self._read_bridge_enabled()

        return self._request_bridge

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
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            self._async_put(url,
                            record['uid'],
                            record,
                            bridge_mode=self._request_bridge)

    def spread_delete(self, uid):
        """
        Spreads a delete call in the background
        :param uid: str
        """
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            self._async_delete(url,
                               uid,
                               bridge_mode=self._request_bridge)

    @classmethod
    def _put_job(cls, url, dirs, params, data):
        """Puts result data job
        """
        Helpers.request_put(url=url, dirs=dirs, data=data, params=params)

    def _cache_put_job(self, url, dirs, params, data):
        """Puts request data job for cached from mode
        """
        response = Helpers.request_put(url=url,
                                       dirs=dirs,
                                       data=data,
                                       params=params)

        if response.status_code == 200:
            self._append_cache_input(content=response.content)

    def _append_cache_input(self, content):
        """Appends the response content into cache
        """
        record = json.loads(content)
        self._cache_inputs.put(record)

        while not self._cache_inputs.empty():
            input_record = self._cache_inputs.get()
            self._cache.put(input_record)

    def _async_put(self, url, uid, record, bridge_mode):
        content = json.dumps(record)

        data = {'value': content}
        params = {MIRROR_MODE: int(True)}

        if bridge_mode:
            params[BRIDGE_MODE] = int(True)

        start_new_thread(self._put_job, (url, [uid], params, data))

    @classmethod
    def _delete_job(cls, url, dirs, params):
        Helpers.request_delete(url=url, dirs=dirs, params=params)

    def _async_delete(self, url, uid, bridge_mode):
        params = {MIRROR_MODE: int(True)}

        if bridge_mode:
            params[BRIDGE_MODE] = int(True)

        start_new_thread(self._delete_job, (url, [uid], params))