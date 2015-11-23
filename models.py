#!/usr/bin/env python
"""Models
"""
from abc import ABCMeta, abstractmethod
import time

import sys
sys.path.append('..')

from minstore.exceptions import RecordMissing, RecordExists
from minstore.helpers import Helpers


class Model(object):
    __metaclass__ = ABCMeta

    def __init__(self, **params):
        self._storage = params['storage']
        pass

    @abstractmethod
    def get(self, uid):
        """
        Gets a record from database
        :param uid: str|int
        :return: dict
        """
        pass

    @abstractmethod
    def insert(self, uid, values):
        """
        Inserts a new record
        :param uid: str
        :param values: dict
        :return: dict
        """
        pass

    @abstractmethod
    def update(self, uid, values):
        """
        Updates a record.
        :param uid: str
        :param values: dict
        :return: dict
        """
        pass

    @abstractmethod
    def delete(self, uid):
        """
        Deletes record on database
        :param uid: str|int
        """
        pass

    def _valid_exists(self, uid):
        """
        Checks if record exists. Raises an exception if does not.
        :param uid: str
        :return: bool
        """
        if not self._storage.exists(uid=uid):

            raise RecordMissing(
                'Select Error: Record {!s} is missing'.format(uid))

    def _valid_no_exists(self, uid):
        """
        Checks if record no exists. Raises an exception if does.
        :param uid: str
        :return: bool
        """
        if self._storage.exists(uid=uid):

            raise RecordExists(
                'Insert Error: Record {!s} already exists'.format(uid))


class TextModel(Model):
    """Text Model"""

    def __init__(self, **params):
        super(TextModel, self).__init__(**params)
        self._processes = params['processes']

    def get(self, uid):
        """
        Retrieves a Text from database
        :param uid: str
        :return: dict
        """
        self._valid_exists(uid=uid)

        record = self._storage.select(uid=uid)

        return record

    def delete(self, uid):
        """
        Deletes a Text from database
        :param uid: str
        """
        self._valid_exists(uid=uid)

        self._storage.delete(uid=uid)

    def insert(self, uid, values):
        """
        Inserts a new record
        :param uid: str
        :param values: dict
        :return: dict
        """
        text = values['value']
        self._valid_no_exists(uid=uid)

        record = self.create(uid=uid,
                             value=text,
                             processes=self._processes)

        self._storage.insert(record=record)

        return record

    def update(self, uid, values):
        """
        Updates a record. Raises an exception if record exists
        :param uid: str
        :param values: dict
        :return: dict
        """
        text = values['value']

        self._valid_exists(uid=uid)

        last_check_sum = self.get_check_sum(uid=uid)

        new_check_sum = Helpers.sign(text)

        if last_check_sum == new_check_sum:
            raise RecordExists('Record has no change')

        record = self.create(uid=uid,
                             value=text,
                             check_sum=new_check_sum,
                             processes=self._processes)

        self._storage.update(record=record)

        return record

    def copy(self, record):
        """
        Forces to create or update a record. Acts as mirror.
        :param record: dict
        :return: dict
        """
        self._storage.update(record=record)

        return record

    def get_check_sum(self, uid):
        """
        Retrieves the check_sum of a record.
        :param uid: str
        :return: str
        """
        values = self._storage.select(uid=uid)

        return values['check_sum']

    @classmethod
    def create(cls, uid, value, check_sum=None, processes=list()):
        """
        Creates, processes and returns a record
        :param uid: str
        :param value: str
        :param check_sum: str
        :param processes: list
        :return: object
        """
        record = dict()
        record['uid'] = uid
        record['value'] = value
        record['timestamp'] = time.time()

        if not check_sum:
            check_sum = Helpers.sign(value)

        record['check_sum'] = check_sum

        for process in processes:
            process.process(record)

        record['size'] = Helpers.iterable_size(target=record)

        return record
