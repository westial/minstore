#!/usr/bin/env python
"""Classes for application instances distribution within infrastructure
"""
import json
from thread import start_new_thread

from minstore.constants import *
from minstore.exceptions import ServerMissing, RecordMissing
from minstore.helpers import Helpers, RecordHelper


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

        self._load_servers()
        self._set_bridge_request()

    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, instance):
        self._cache = instance
        self._validate_cache_config()

    def _validate_cache_config(self):
        """Validates cache config and returns True if it is fine or raises an
        exception on wrong configuration is found.
        :raise ServerMissing
        :return bool
        """
        if self._cache.is_enabled and not len(self._servers):
            raise ServerMissing('Cache requires at least one dependant server')

        return True

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

    def _bounce_delete_job(self, url, uid, params=None):
        """
        Requests a delete job given an url, uid and value, and optionally a
        get url parameters.

        Returns False if response code is not 200.

        :param url: str
        :param uid: str
        :param params: dict
        :return: bool
        """
        response = Helpers.request_delete(
            url=url,
            dirs=[uid],
            params=params,
        )

        if response.status_code != 200:
            return False

        try:
            self._cache.forget(uid=uid)

        finally:
            return True

    def bounce_delete(self, uid):
        """
        Bounces a delete request to all dependants. Deletes the record from
        cache.
        :param uid: str
        :raise RecordMissing
        """
        deleted = False
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            deleted = self._bounce_delete_job(url=url, uid=uid)

        if not deleted:
            raise RecordMissing()

        return

    def _bounce_put_job(self, url, uid, value, to_cache=False, params=None):
        """
        Requests a put job given an url, uid and value, and optionally a
        get url parameters.

        Optionally updates the record into cache.

        Returns False if response code is not 200. Converts the response
        content into a valid record if possible and returns the record on
        success.

        :param url: str
        :param uid: str
        :param value: str
        :param to_cache: bool. If True records the response into cache.
        :param params: dict
        :return: dict
        """
        response = Helpers.request_put(
            url=url,
            dirs=[uid],
            data={'value': value},
            params=params,
        )

        record = RecordHelper.str2record(content=response.content)

        if response.status_code != 200 or not record:
            return False

        if to_cache:
            self._cache.put(record)

        return record

    def bounce_put(self, uid, value):
        """
        Bounces a put request to all dependants. Records the first valid
        response content into the cache. Returns the record got from dependants.
        :param uid: str
        :param value: str
        :return dict
        """
        valid_response = None
        record = None
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            record = self._bounce_put_job(url=url,
                                          uid=uid,
                                          value=value,
                                          to_cache=valid_response)
            valid_response = bool(record)

        return record

    def _bounce_post_job(self, url, uid, value, to_cache=False, params=None):
        """
        Requests a post job given an url, uid and value, and optionally a
        get url parameters.

        Optionally inserts the record into cache.

        Returns False if response code is not 200. Converts the response
        content into a valid record if possible and returns the record on
        success.

        :param url: str
        :param uid: str
        :param value: str
        :param to_cache: bool. If True records the response into cache.
        :param params: dict
        :return: dict
        """
        response = Helpers.request_post(
            url=url,
            dirs=[uid],
            data={'value': value},
            params=params,
        )

        record = RecordHelper.str2record(content=response.content)

        if response.status_code != 200 or not record:
            return False

        if to_cache:
            self._cache.put(record)

        return record

    def bounce_post(self, uid, value):
        """
        Bounces a post request to all dependants. Records the first valid
        response content into the cache. Returns the record got from dependants.
        :param uid: str
        :param value: str
        :return dict
        """
        valid_response = None
        record = None
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            record = self._bounce_post_job(url=url,
                                           uid=uid,
                                           value=value,
                                           to_cache=valid_response)
            valid_response = bool(record)

        return record

    @classmethod
    def _bounce_get_job(cls, url, uid, params=None):
        """
        Requests a get job given an url and uid, and optionally a set of url
        parameters.

        Returns False if response code is not 200. Converts the response
        content into a valid record if possible and returns the record on
        success.

        :param url: str
        :param uid: str
        :param params: dict
        :return: dict
        """
        response = Helpers.request_get(url=url, dirs=[uid], params=params)

        record = RecordHelper.str2record(content=response.content)

        if response.status_code != 200 or not record:
            return False

        return record

    def bounce_get(self, uid):
        """
        Looks for the uid within all dependant servers.
        :param uid: str
        :return: dict
        """
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            record = self._bounce_get_job(url=url, uid=uid)
            if record:
                return record

        raise RecordMissing()

    def spread_put(self, record):
        """
        Spreads a put call in the background.
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
    def _valid_cache_request(cls, response):
        """Validates the prepared cache request
        """
        if response.status_code != 200:
            return False

        if not len(response.content):
            return False

        return True

    @classmethod
    def _put_job(self, url, dirs, params, data):
        """Puts result data job
        """
        Helpers.request_put(url=url,
                            dirs=dirs,
                            data=data,
                            params=params)

    def _async_put(self, url, uid, record, bridge_mode):
        content = json.dumps(record)

        data = {'value': content}
        params = {MIRROR_MODE: int(True)}

        if bridge_mode:
            params[BRIDGE_MODE] = int(True)

        start_new_thread(self._put_job, (url, [uid], params, data))

    def _delete_job(self, url, dirs, params):
        Helpers.request_delete(url=url, dirs=dirs, params=params)

        uid = dirs[-1]
        self._cache.forget(uid=uid)

    def _async_delete(self, url, uid, bridge_mode):
        params = {MIRROR_MODE: int(True)}

        if bridge_mode:
            params[BRIDGE_MODE] = int(True)

        start_new_thread(self._delete_job, (url, [uid], params))
