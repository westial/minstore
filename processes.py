#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Processes for text
"""
import random
from abc import abstractmethod, ABCMeta


class Process(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        """
        Constructor
        """

    @classmethod
    @abstractmethod
    def process(cls, record):
        """
        Processes a record
        :param record: dict
        """


class DetectLangProcess(Process):

    @classmethod
    def process(cls, record):
        """
        Detects language and sets on record
        :param record: dict
        :return:
        """
        record['lang'] = cls.detect_lang()

    @classmethod
    def detect_lang(cls):
        """
        Returns the language "strictly".
        :return: str
        """
        languages = ['en', 'es', 'ct', 'fr', 'jp', 'it', 'de']
        return random.choice(languages)


class MarkProcess(Process):

    @classmethod
    def process(cls, record):
        """
        Marks the text of a record.
        :param record: dict
        """
        record['value'] += ' (Marked).'
