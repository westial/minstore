#!/usr/bin/env python
"""Persistence engine
"""

from abc import ABCMeta, abstractmethod
import json

import sys
sys.path.append('..')

from minstore.helpers import Helpers


class Storage(object):
    __metaclass__ = ABCMeta

    def __init__(self, **params):
        pass

    @abstractmethod
    def select(self, uid):
        """
        Select query for database
        :param uid: str|int
        :return: dict
        """
        pass

    @abstractmethod
    def insert(self, **params):
        """
        Insert query for database
        """
        pass

    @abstractmethod
    def update(self, **params):
        """
        Update query for database
        """
        pass

    @abstractmethod
    def delete(self, uid):
        """
        Delete query for database
        :param uid: str|int
        """
        pass


class FileStorage(Storage):
    """
    Engine for a storage based on files
    """

    def __init__(self, **params):
        """
        Constructor
        """
        super(FileStorage, self).__init__(**params)

        self._base_path = params['base_path']
        self._file = None

    def update(self, record):
        file_path = self.__format_filename(filename=record['uid'],
                                           base_path=self._base_path)
        with open(file_path, 'wb+') as self._file:
            self._write(record=record)

    def insert(self, record):
        file_path = self.__format_filename(filename=record['uid'],
                                           base_path=self._base_path)
        with open(file_path, 'wb+') as self._file:
            self._write(record=record)

    def select(self, uid):
        file_path = self.__format_filename(filename=uid,
                                           base_path=self._base_path)
        with open(file_path, 'rb') as self._file:
            record = self._read()

        return record

    def delete(self, uid):
        self._remove_file_by_uid(uid=uid)

    def _read(self):
        """
        Reads the file and returns the content formatted as expected record
        :return dict
        """
        content = self._file.read()
        record = json.loads(content)

        return record

    def _write(self, record):
        """
        Writes a formatted record to the file
        :param record: dict
        """
        content = json.dumps(record)

        self._file.write(content)

    def exists(self, uid):
        """
        Checks if a record exists and returns True or False.
        :param uid: str
        :return: bool
        """
        file_path = self.__format_filename(filename=uid,
                                           base_path=self._base_path)

        return Helpers.path_exists(file_path)

    def _remove_file_by_uid(self, uid):
        """
        Removes the file
        :param uid: str
        """
        file_path = self.__format_filename(filename=uid,
                                           base_path=self._base_path)

        return Helpers.delete_file(file_path=file_path)

    @classmethod
    def __format_filename(cls, filename, base_path):
        """
        :param filename: str
        :param base_path: str
        :return: str
        """
        file_path = '{!s}/{!s}'.format(base_path, filename)

        return file_path
