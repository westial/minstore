#!/usr/bin/env python
"""API's for all domain cores
"""
import json
from wsgiservice import *
from wsgiref.simple_server import make_server
from thread import start_new_thread

import sys

sys.path.append('..')

from minstore.about import AboutHelper
from minstore.exceptions import RecordExists
from minstore.exceptions import RecordMissing
from minstore.models import TextModel
from minstore.storage import FileStorage
from minstore.processes import DetectLangProcess, MarkProcess
from minstore.helpers import Helpers

DEFAULT_PORT = 8001

MIRROR_MODE = 'mirror'
BRIDGE_MODE = 'bridge'

# Globals

storage = None
model = None
spread = None
base_path = None
servers_list_path = None


class Spread(object):
    """Class spreading to mirrors
    """

    def __init__(self, config_path, route=''):
        """Constructor
        """
        self._config_path = config_path
        self._route = route
        self._servers = list()

        self._load_servers()

    def _load_servers(self):
        with open(self._config_path, 'rb') as config_file:
            content = config_file.read()
            self._servers = content.split()

    def _read_bridge_enabled(self):
        """
        Checks the bridge mode in servers list.
        :return: bool
        """
        if self._servers[0] == '*':
            self._servers.pop(0)
            return True

        else:
            return False

    def spread_put(self, record):
        """
        Spreads a put call in the background
        :param record: dict
        """
        bridge_mode = self._read_bridge_enabled()
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            self._async_put(url, record['uid'], record, bridge_mode=bridge_mode)

    def spread_delete(self, uid):
        """
        Spreads a delete call in the background
        :param uid: str
        """
        bridge_mode = self._read_bridge_enabled()
        for url in self._servers:
            url = '{!s}/{!s}'.format(url, self._route)
            self._async_delete(url, uid, bridge_mode=bridge_mode)

    @classmethod
    def _put_job(cls, url, dirs, params, data):
        Helpers.request_put(url=url, dirs=dirs, data=data, params=params)

    def _async_put(self, url, uid, record, bridge_mode):
        content = json.dumps(record)

        data = {'value': content}
        params = {MIRROR_MODE: True}

        if bridge_mode:
            params[BRIDGE_MODE] = True

        start_new_thread(self._put_job, (url, [uid], params, data))

    @classmethod
    def _delete_job(cls, url, dirs, params):
        Helpers.request_delete(url=url, dirs=dirs, params=params)

    def _async_delete(self, url, uid, bridge_mode):
        params = {MIRROR_MODE: True}

        if bridge_mode:
            params[BRIDGE_MODE] = True

        start_new_thread(self._delete_job, (url, [uid], params))


# API


@mount('/text/{uid}')
class TextApi(Resource):

    NOT_FOUND = (KeyError,)
    __etag = None

    def GET(self, uid):
        """Returns a text by its uid.
        :param uid: str
        """
        try:
            values = self._model.get(uid=uid)
            self.__set_etag(uid, values['check_sum'])

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

            if not self._is_mirror or self._is_bridge:

                values = self._model.update(uid=uid, values={'value': value})

                self._spread.spread_put(record=values)

            else:
                values = self._copy_input(content=value)

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
            values = self._model.insert(uid=uid, values={'value': value})

            self._spread.spread_put(record=values)

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

                self._spread.spread_delete(uid=uid)

        except KeyError, exc:
            raise_400(self, exc.message)

        except TypeError, exc:
            raise_400(self, exc.message)

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
        record = json.loads(content)
        self._model.copy(record=record)

        return record

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
    def _spread(self):
        """Gets the spread, it creates the spread engine if not exists"""
        global spread, servers_list_path

        if not spread:
            spread = Spread(config_path=servers_list_path, route='text')

        return spread

    def __set_etag(self, action, uid):
        """Sets the value for the etag"""
        self.__etag = '{action}-{uid}'.format(action=action, uid=uid)


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
