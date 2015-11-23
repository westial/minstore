#!/usr/bin/env python
"""Custom exceptions
"""


class RecordExists(Exception):
    """Exception raised when the record exists"""

    def __init__(self, message='Record exists'):

        super(Exception, self).__init__(message)


class RecordMissing(Exception):
    """Exception raised when the record is missing"""

    def __init__(self, message='Record is missing'):

        super(Exception, self).__init__(message)


class OverCacheSize(Exception):
    """Exception raised when the record is bigger than cache size"""

    def __init__(self, message='Record exceeds cache space'):

        super(Exception, self).__init__(message)
