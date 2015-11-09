#!/usr/bin/env python
"""Services and helpers
"""
import os
import requests


class Helpers(object):

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
    def request_post(cls, url, params, data, timeout=30):
        url = '{!s}/{!s}'.format(url, '/'.join(params))
        response = requests.post(url, data=data, timeout=timeout)
        return response

    @classmethod
    def request_put(cls, url, params, data, timeout=30):
        url = '{!s}/{!s}'.format(url, '/'.join(params))
        response = requests.put(url, data=data, timeout=timeout)
        return response

    @classmethod
    def request_get(cls, url, params, data=None, timeout=30):
        url = '{!s}/{!s}'.format(url, '/'.join(params))
        response = requests.get(url, params=data, timeout=timeout)
        return response

    @classmethod
    def request_delete(cls, url, params, data=None, timeout=30):
        url = '{!s}/{!s}'.format(url, '/'.join(params))
        response = requests.delete(url, params=data, timeout=timeout)
        return response
