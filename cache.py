#!/usr/bin/env python
"""Classes for caching
"""
from abc import ABCMeta, abstractmethod
from Queue import Queue
from threading import RLock

from minstore.exceptions import RecordMissing

UNLIMITED_MEMORY = -1
DISABLED_MEMORY = 0


class Cache(object):
    __metaclass__ = ABCMeta

    def __init__(self, size_limit=UNLIMITED_MEMORY):
        """Constructor
        """
        self._size_limit = size_limit
        self._buffer = dict()
        self._buffer_size = 0

    @abstractmethod
    def put(self, what):
        """Records the given data to the cache. Returns True if done else False.
        :param what: dict
        """
        pass

    @abstractmethod
    def get(self, **params):
        """Gets a cache input
        """
        pass

    @abstractmethod
    def forget(self, **params):
        """Deletes a cache record
        """
        pass

    @abstractmethod
    def is_enabled(self):
        """Checks enabled
        """
        pass

    def _enough_memory(self, record_size):
        """Checks if there is enough cache memory for the record size.
        :return bool
        """
        if self._size_limit == UNLIMITED_MEMORY:
            return True

        if record_size > self._size_limit:
            return False

        return True

    @abstractmethod
    def _exists(self, record):
        """Checks if the record already exists in buffer. If record already
        exists returns True else False
        """
        pass

    def _decrease_buffer_size(self, size):
        """Decreases the size value of the buffer
        :param size: double
        """
        self._buffer_size -= size

    def _increase_buffer_size(self, size):
        """Increases the size value of the buffer
        :param size: double
        """
        self._buffer_size += size


class MemoryCache(Cache):
    """Class for cache management.
    """

    def __init__(self, size_limit=UNLIMITED_MEMORY):
        """Constructor

        :param size_limit: int maximum number of bytes of dedicated cache
        memory. If size_limit is -1, the memory is unlimited. If size_limit is 0
        the cache is disabled and does not allow get or put.
        """
        super(MemoryCache, self).__init__(size_limit=size_limit)
        self._waiting_cache = Queue()
        self._buffer_lock = RLock()

    def is_enabled(self):
        return self._size_limit != DISABLED_MEMORY

    def put(self, record):
        if not self.is_enabled():
            return None

        if not self._enough_memory(record_size=record['size']):
            return False

        if self._exists(record=record):
            return False

        self._waiting_cache.put(record)

        while not self._waiting_cache.empty():

            record = self._waiting_cache.get()
            self._free_memory(record_size=record['size'])
            self.__append_cache(record=record)

        return True

    def get(self, **params):
        if not self.is_enabled():
            return None

        return self.__get_cache(uid=params['uid'])

    def forget(self, **params):
        if not self.is_enabled():
            return None

        return self.__forget_cache(uid=params['uid'])

    def __append_cache(self, record):
        """Appends a new record to the thread safe cache dictionary.
        :param record: dict
        """
        self._buffer_lock.acquire()

        try:
            self._buffer[record['uid']] = record
            self._increase_buffer_size(size=record['size'])

        finally:
            self._buffer_lock.release()

        return True

    def __get_cache(self, uid):
        """Returns a record of the thread safe cache dictionary by uid.
        :param uid: str
        :raise RecordMissing
        """
        self._buffer_lock.acquire()

        try:
            record = self._buffer[uid]

        except KeyError:
            raise RecordMissing()

        finally:
            self._buffer_lock.release()

        return record

    def __forget_cache(self, uid):
        """Deletes a record of the thread safe cache dictionary by uid.
        :param uid: str
        :raise RecordMissing
        """
        self._buffer_lock.acquire()

        try:
            del self._buffer[uid]

        except KeyError:
            raise RecordMissing()

        finally:
            self._buffer_lock.release()

    def _exists(self, record):
        try:
            existing = self.__get_cache(uid=record['uid'])

            if existing['check_sum'] == record['check_sum']:
                return True

        except RecordMissing:
            return False

        return False

    def _free_memory(self, record_size):
        """Removes items of cache until the memory of the cache is under the
        maximum cache size.

        :param record_size: int
        """
        while record_size + self._buffer_size > self._size_limit:

            record_left = self._buffer.pop(self._buffer.keys()[0])
            self._decrease_buffer_size(size=record_left['size'])

        return True
