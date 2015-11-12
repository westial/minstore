#!/usr/bin/env python
"""Basic test cases
"""
import json
import os
import time
import unittest2
import uuid
from threading import Thread

import sys
sys.path.append('..')

from minstore.helpers import Helpers

URL = 'http://127.0.0.1:8010'

URL1 = 'http://127.0.0.1:8001'
URL2 = 'http://127.0.0.1:8002'
URL3 = 'http://127.0.0.1:8003'


class TestCases(unittest2.TestCase):
 
    def setUp(self):
        self.sample_normal = {
            'uid': None,
            'value': "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
        }
        self.sample_fixed = {
            'uid': 'fixed-identifier',
            'value': "this text can be inserted and after deleted using its easy uid"
        }
        self.sample_fixed_len = {
            'uid': 'fixed-len-identifier',
            'value': "0123456789"
        }
        self.threads = list()

        self.start_server(servers_list_path='test-sandbox/simple/servers.list',
                          base_path='test-sandbox/simple',
                          port=8010)

        time.sleep(10)

        pass

    def tearDown(self):
        self.stop_all_apis()

    def stop_all_apis(self):
        """
        Stops all wsgiservice apis and threads
        """
        os.system('pkill -f "python api.py"')

        while len(self.threads):
            thread = self.threads.pop()
            thread.join()

    def start_server(self, servers_list_path, base_path, port):
        """
        Starts an api server into a separated thread
        :param port: int
        """
        thread = Thread(target=self.async_api,
                        args=[servers_list_path, base_path, port])
        thread.start()
        self.threads.append(thread)

    def async_api(self, servers_list_path, base_path, port):
        """
        Asynchronous task starting the wsgiservice.
        :param servers_list_path: str
        :param base_path: str
        :param port: int
        """
        os.system("python api.py {!s} {!s} {:d}".format(servers_list_path,
                                                        base_path,
                                                        port))

    def new_uid(self):
        return str(uuid.uuid4())

    def get_record_by_path(self, file_path):
        """
        Retrieves a record from a file
        :param file_path: str
        :return: dict
        """
        with open(file_path, 'rb+') as record_file:
            content = record_file.read()

        record = json.loads(content)
        return record

    def get_record_by_response_content(self, content):
        """
        Retrieves a record for a given request response
        :param content: str
        :return: dict
        """
        record = json.loads(content)
        return record

    def test_mirror(self):
        self.start_server(servers_list_path='test-sandbox/mirror/mirror1/servers.list',
                          base_path='test-sandbox/mirror/mirror1',
                          port=8001)

        self.start_server(servers_list_path='test-sandbox/mirror/mirror2/servers.list',
                          base_path='test-sandbox/mirror/mirror2',
                          port=8002)

        self.start_server(servers_list_path='test-sandbox/mirror/mirror3/servers.list',
                          base_path='test-sandbox/mirror/mirror3',
                          port=8003)
        time.sleep(10)

        uid = self.sample_fixed['uid']
        value = self.sample_fixed['value']
        response = Helpers.request_post(
            url=URL1,
            dirs=['text', uid],
            data={'value': value})
        self.assertEqual(response.status_code, 200)

        time.sleep(10)

        record1 = self.get_record_by_path('test-sandbox/mirror/mirror1/' + uid)
        record2 = self.get_record_by_path('test-sandbox/mirror/mirror2/' + uid)
        record3 = self.get_record_by_path('test-sandbox/mirror/mirror3/' + uid)

        self.assertEqual(record1, record2, 'POST: Record 1 and 2')
        self.assertEqual(record2, record3, 'POST: Record 2 and 3')
        self.assertEqual(record1['uid'], uid, 'POST: Unexpected uid')

        value = 'I have changed the content on first and mirror site too.'
        response = Helpers.request_put(
            url=URL1,
            dirs=['text', uid],
            data={'value': value})
        self.assertEqual(response.status_code, 200)

        response_record = self.get_record_by_response_content(response.content)

        self.assertEqual(response_record['value'][0:20], value[0:20])

        time.sleep(10)

        record1 = self.get_record_by_path('test-sandbox/mirror/mirror1/' + uid)
        record2 = self.get_record_by_path('test-sandbox/mirror/mirror2/' + uid)
        record3 = self.get_record_by_path('test-sandbox/mirror/mirror3/' + uid)

        self.assertEqual(record1, record2, 'PUT: Record 1 and 2')
        self.assertEqual(record2, record3, 'PUT: Record 2 and 3')
        self.assertEqual(record1['uid'], uid, 'PUT: Unexpected uid')

        response = Helpers.request_delete(
            url=URL1,
            dirs=['text', uid])

        self.assertEqual(response.status_code, 200)

        time.sleep(10)

        exists1 = Helpers.path_exists('test-sandbox/mirror/mirror1/' + uid)
        exists2 = Helpers.path_exists('test-sandbox/mirror/mirror2/' + uid)
        exists3 = Helpers.path_exists('test-sandbox/mirror/mirror3/' + uid)

        self.assertFalse(exists1)
        self.assertFalse(exists2)
        self.assertFalse(exists3)

        self.stop_all_apis()

    def test_get_not_exists_error(self):
        response = Helpers.request_get(
            url=URL,
            dirs=['text', self.new_uid()])

        self.assertEqual(response.status_code, 404)

    def test_delete_not_exists_error(self):
        response = Helpers.request_delete(
            url=URL,
            dirs=['text', self.new_uid()])

        self.assertEqual(response.status_code, 404)

    def test_post_exists_error(self):
        uid = self.new_uid()
        response = Helpers.request_post(
            url=URL,
            dirs=['text', uid],
            data={'value': self.sample_normal['value']})

        self.assertEqual(response.status_code, 200, 'First Post failed')

        response = Helpers.request_post(
            url=URL,
            dirs=['text', uid],
            data={'value': self.sample_normal['value']})

        self.assertEqual(response.status_code, 400, 'Repeated Post failed')

        response = Helpers.request_delete(
            url=URL,
            dirs=['text', uid])

        self.assertEqual(response.status_code, 200, 'Delete failed')

    def test_put_not_exists_error(self):
        response = Helpers.request_put(
            url=URL,
            dirs=['text', self.new_uid()],
            data={'value': 'dummy content'})

        self.assertEqual(response.status_code, 404)

    def test_get_exists(self):
        uid = self.sample_fixed_len['uid']
        expected_len = 180
        response = Helpers.request_post(
            url=URL,
            dirs=['text', uid],
            data={'value': self.sample_fixed_len['value']})
        self.assertEqual(response.status_code, 200, 'Post failed')

        response = Helpers.request_get(
            url=URL,
            dirs=['text', uid])

        self.assertEqual(response.status_code, 200, 'Get failed')
        self.assertGreaterEqual(len(response.content), expected_len)
        self.assertLessEqual(len(response.content), expected_len + 1)

        response = Helpers.request_delete(
            url=URL,
            dirs=['text', uid])

        self.assertEqual(response.status_code, 200, 'Delete failed')
 
    def test_post_new(self):
        uid = self.new_uid()
        response = Helpers.request_post(
            url=URL,
            dirs=['text', uid],
            data={'value': self.sample_normal['value']})
        self.assertEqual(response.status_code, 200, 'Post failed')

        response = Helpers.request_delete(
            url=URL,
            dirs=['text', uid])

        self.assertEqual(response.status_code, 200, 'Delete failed')

    def test_delete_exists(self):
        uid = self.new_uid()
        response = Helpers.request_post(
            url=URL,
            dirs=['text', uid],
            data={'value': self.sample_normal['value']})

        self.assertEqual(response.status_code, 200)

        response = Helpers.request_delete(
            url=URL,
            dirs=['text', uid])

        self.assertEqual(response.status_code, 200)

    def test_put_exists(self):
        first_content = self.sample_fixed['value']
        second_content = 'New content.'

        response = Helpers.request_post(
            url=URL,
            dirs=['text', self.sample_fixed['uid']],
            data={'value': first_content})

        self.assertEqual(response.status_code, 200, 'First post failed')

        first_len = len(response.content)
        difference = len(second_content) - len(first_content)
        expected_second_len = first_len + difference

        response = Helpers.request_put(
            url=URL,
            dirs=['text', self.sample_fixed['uid']],
            data={'value': 'New content.'})

        self.assertEqual(response.status_code, 200, 'Put failed')

        second_len = len(response.content)

        second_len -= 1     # Due to optional negative sign on check_sum

        self.assertLessEqual(second_len, expected_second_len)

        response = Helpers.request_delete(
            url=URL,
            dirs=['text', self.sample_fixed['uid']])

        self.assertEqual(response.status_code, 200, 'Delete failed')

 
if __name__ == '__main__':
    unittest2.main()
