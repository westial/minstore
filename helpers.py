#!/usr/bin/env python
"""Services and helpers
"""
from binascii import hexlify
import os
import requests


class Helpers(object):

    @classmethod
    def iterable_size(cls, target):
        """
        Returns the bytes length size of an iterable object
        :param target: dict
        :return: int
        """
        target_len = 0

        for item in target:
            target_len += len(hexlify(str(item)))
            target_len += len(hexlify(str(target[item])))

        return target_len

    @classmethod
    def sign(cls, hashable):
        """
        Returns a hash as sign of the given object
        :param hashable: mixed
        :return str
        """
        return hash(hashable)

    @classmethod
    def path_exists(cls, path):
        """
        Checks if path exists
        :param path: str
        :return: bool
        """
        try:
            return bool(os.stat(path))

        except OSError:
            return False

    @classmethod
    def file_size(cls, target):
        """
        Returns the file size
        :param target: file
        :return: int
        """
        target.seek(0, os.SEEK_END)
        size = target.tell()

        return size

    @classmethod
    def delete_file(cls, file_path):
        """
        Removes the file
        """
        os.remove(file_path)

    @classmethod
    def __get_request_headers(cls):
        """
        Returns a dict of common request HTTP headers
        :return: dict
        """
        headers = {'Accept': 'application/json'}

        return headers

    @classmethod
    def request_post(cls, url, dirs, data, params=None, timeout=30):
        """
        Makes a post request.
        :param url: destination url
        :param dirs: route path items
        :param data: post data
        :param params: URI query params
        :param timeout: timeout seconds for request
        :return: HTTP response
        """
        url = '{!s}/{!s}'.format(url, '/'.join(dirs))
        headers = cls.__get_request_headers()
        response = requests.post(url,
                                 data=data,
                                 params=params,
                                 timeout=timeout,
                                 headers=headers)
        return response

    @classmethod
    def request_put(cls, url, dirs, data, params=None, timeout=30):
        """
        Makes a put request.
        :param url: destination url
        :param dirs: route path items
        :param data: post data
        :param params: URI query params
        :param timeout: timeout seconds for request
        :return: HTTP response
        """
        url = '{!s}/{!s}'.format(url, '/'.join(dirs))
        headers = cls.__get_request_headers()
        response = requests.put(url,
                                data=data,
                                params=params,
                                timeout=timeout,
                                headers=headers)
        return response

    @classmethod
    def request_get(cls, url, dirs, params=None, timeout=30):
        """
        Makes a get request.
        :param url: destination url
        :param dirs: route path items
        :param params: URI query params
        :param timeout: timeout seconds for request
        :return: HTTP response
        """
        url = '{!s}/{!s}'.format(url, '/'.join(dirs))
        headers = cls.__get_request_headers()
        response = requests.get(url,
                                params=params,
                                timeout=timeout,
                                headers=headers)
        return response

    @classmethod
    def request_delete(cls, url, dirs, params=None, timeout=30):
        """
        Makes a delete request.
        :param url: destination url
        :param dirs: route path items
        :param params: URI query params
        :param timeout: timeout seconds for request
        :return: HTTP response
        """
        url = '{!s}/{!s}'.format(url, '/'.join(dirs))
        response = requests.delete(url, params=params, timeout=timeout)
        return response
