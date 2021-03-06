#!/usr/bin/env python
"""API's for all domain cores
"""
from wsgiservice import *
from wsgiref.simple_server import make_server

import sys
from minstore.cache import MemoryCache
from minstore.strategies import Spread

sys.path.append('..')

from minstore.constants import *
from minstore.about import AboutHelper
from minstore.exceptions import RecordExists
from minstore.exceptions import RecordMissing
from minstore.models import TextModel
from minstore.storage import FileStorage
from minstore.processes import DetectLangProcess, MarkProcess
from minstore.helpers import Helpers, RecordHelper

# Globals

storage = None
model = None
strategy = None
base_path = None
servers_list_path = None


@mount('/text/{uid}')
class TextApi(Resource):

    NOT_FOUND = (KeyError,)
    __etag = None

    def GET(self, uid):
        """Returns a text by its uid.
        First checks cache if enabled. Second checks local storage and third
        looks for it into dependant servers.

        :param uid: str
        :return dict
        """
        try:
            values = None

            if self._strategy.cache:
                values = self._strategy.cache.get(uid=uid)

            if not values:
                values = self._model.get(uid=uid)

            self.__set_etag(uid, values['check_sum'])
            return values

        except RecordMissing:
            try:
                values = self._strategy.bounce_get(uid=uid)

                return values

            except RecordMissing:
                raise_404(self)

        except Exception, exc:
            raise_500(self, exc.message)

    def PUT(self, uid):
        """Updates a record by uid.
        :param uid: str
        """
        try:
            value = self.request.POST['value']

            if self._is_cache:
                values = self._strategy.bounce_put(uid=uid, value=value)

            else:

                if not self._is_mirror:
                    values = self._model.update(uid=uid, values={'value': value})

                else:
                    values = self._copy_input(content=value)

                if values and (not self._is_mirror or self._is_bridge):

                    self._strategy.spread_put(record=values)

            return values

        except KeyError, exc:
            raise_400(self, exc.message)

        except TypeError, exc:
            raise_400(self, exc.message)

        except RecordMissing:
            raise_404(self)

        except Exception, exc:
            raise_500(self, exc.message)

    def POST(self, uid):
        """Creates a record with uid.
        :param uid: str
        """
        try:
            value = self.request.POST['value']

            if self._is_cache:
                values = self._strategy.bounce_post(uid=uid, value=value)

            else:
                values = self._model.insert(uid=uid, values={'value': value})
                self._strategy.spread_put(record=values)

            return values

        except KeyError, exc:
            raise_400(self, exc.message)

        except TypeError, exc:
            raise_400(self, exc.message)

        except RecordExists:
            raise_400(self)

        except Exception, exc:
            raise_500(self, exc.message)

    def DELETE(self, uid):
        """Delete the document by uid.
        :param uid: str
        """
        try:
            self._model.delete(uid=uid)

            if not self._is_mirror or self._is_bridge:

                self._strategy.spread_delete(uid=uid)

        except KeyError, exc:
            raise_400(self, exc.message)

        except TypeError, exc:
            raise_400(self, exc.message)

        except RecordMissing:
            try:
                self._strategy.bounce_delete(uid=uid)

            except RecordMissing:
                raise_404(self)

        except Exception, exc:
            raise_500(self, exc.message)

    def get_etag(self):
        return self.__etag

    def _copy_input(self, content):
        """
        Given a formatted json string updates the record related to.
        :param content: str
        :return: dict
        """
        record = RecordHelper.str2record(content=content)

        if not record:
            return None

        self._model.copy(record=record)

        return record

    @property
    def _is_cache(self):
        """
        Checks if request is for mode cache storing only.
        :return: bool
        """
        return CACHE_MODE in self.request.GET

    @property
    def _is_mirror(self):
        """
        Checks if request is for mode mirror.
        :return: bool
        """
        return MIRROR_MODE in self.request.GET

    @property
    def _is_bridge(self):
        """
        Checks if request is for mode bridge.
        :return: bool
        """
        return BRIDGE_MODE in self.request.GET

    @property
    def _storage(self):
        """Gets the storage, it creates the storage if not exists"""
        global storage, base_path

        if not storage:
            storage = FileStorage(base_path=base_path)

        return storage

    @property
    def _model(self):
        """Gets the text model, it creates the model if not exists"""
        global model, storage
        processes = [DetectLangProcess, MarkProcess]

        if not model:
            model = TextModel(storage=self._storage, processes=processes)

        return model

    @property
    def _strategy(self):
        """Gets the persistence strategy, creates it if not exists.
        """
        global strategy, servers_list_path

        if not strategy:
            strategy = Spread(config_path=servers_list_path, route='text')

            if self._is_cache:
                strategy.cache = MemoryCache(size_limit=MAX_CACHE_SIZE_LEN)

        return strategy

    def __set_etag(self, uid, check_sum):
        """Sets the value for the etag
        :param uid: str
        :param check_sum: double
        """
        self.__etag = '{uid}:{check_sum}'.format(uid=uid, check_sum=check_sum)


app = get_app(globals())

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print AboutHelper.help_info(default_port=DEFAULT_PORT)
        exit(1)

    servers_list_path = sys.argv[1]

    if servers_list_path == '-h' or servers_list_path == '--help':
        print AboutHelper.help_info(default_port=DEFAULT_PORT)
        exit(1)

    base_path = sys.argv[2]

    try:
        port = int(sys.argv[3])

    except IndexError:
        port = DEFAULT_PORT

    if not Helpers.path_exists(servers_list_path):
        print "Error: provided SERVERS_LIST_PATH is not a valid path.\n"
        print "See --help for more information.\n"
        exit(1)

    if not Helpers.path_exists(base_path):
        print "Error: provided BASE_PATH is not a valid path.\n"
        print "See --help for more information.\n"
        exit(1)

    print "Running on port {:d}".format(port)
    make_server('', port, app).serve_forever()
