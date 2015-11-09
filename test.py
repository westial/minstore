#!/usr/bin/env python
"""Basic test cases
"""
import unittest2
import uuid

import sys
sys.path.append('..')

from minstore.helpers import Helpers

URL = 'http://localhost:8001/text'


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
        pass

    def new_uid(self):
        return str(uuid.uuid4())

    def test_put_mirroring(self):
        expected_len = 760
        content = '{"lang": "en", "timestamp": 1447037485.564405, "uid": "e528531e-13b2-42fb-a6e7-19fc62c1c499", "value": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum. (Marked).", "check_sum": 3985211366849498588}'

        response = Helpers.request_put(
            url=URL,
            params=['e528531e-13b2-42fb-a6e7-19fc62c1c499'],
            data={'value': content, 'mirroring': True})

        self.assertEqual(response.status_code, 200)

        response_len = len(response.content)

        self.assertEqual(response_len, expected_len, 'Failed Put mirroring')

        response = Helpers.request_delete(
            url=URL,
            params=['e528531e-13b2-42fb-a6e7-19fc62c1c499'])

        self.assertEqual(response.status_code, 200, 'Delete failed')


    def test_delete_mirroring(self):
        uid = self.new_uid()
        response = Helpers.request_post(
            url=URL,
            params=[uid],
            data={'value': self.sample_normal['value']})

        self.assertEqual(response.status_code, 200)

        response = Helpers.request_delete(
            url=URL,
            params=[uid],
            data={'mirroring': True})

        self.assertEqual(response.status_code, 200)

    def test_get_not_exists_error(self):
        response = Helpers.request_get(
            url=URL,
            params=[self.new_uid()])

        self.assertEqual(response.status_code, 404)

    def test_delete_not_exists_error(self):
        response = Helpers.request_delete(
            url=URL,
            params=[self.new_uid()])

        self.assertEqual(response.status_code, 404)

    def test_post_exists_error(self):
        uid = self.new_uid()
        response = Helpers.request_post(
            url=URL,
            params=[uid],
            data={'value': self.sample_normal['value']})

        self.assertEqual(response.status_code, 200, 'First Post failed')

        response = Helpers.request_post(
            url=URL,
            params=[uid],
            data={'value': self.sample_normal['value']})

        self.assertEqual(response.status_code, 400, 'Repeated Post failed')

        response = Helpers.request_delete(
            url=URL,
            params=[uid])

        self.assertEqual(response.status_code, 200, 'Delete failed')

    def test_put_not_exists_error(self):
        response = Helpers.request_put(
            url=URL,
            params=[self.new_uid()],
            data={'value': 'dummy content'})

        self.assertEqual(response.status_code, 404)

    def test_get_exists(self):
        uid = self.sample_fixed_len['uid']
        expected_len = 180
        response = Helpers.request_post(
            url=URL,
            params=[uid],
            data={'value': self.sample_fixed_len['value']})
        self.assertEqual(response.status_code, 200, 'Post failed')

        response = Helpers.request_get(
            url=URL,
            params=[uid])

        self.assertEqual(response.status_code, 200, 'Get failed')
        self.assertGreaterEqual(len(response.content), expected_len)
        self.assertLessEqual(len(response.content), expected_len + 1)

        response = Helpers.request_delete(
            url=URL,
            params=[uid])

        self.assertEqual(response.status_code, 200, 'Delete failed')
 
    def test_post_new(self):
        uid = self.new_uid()
        response = Helpers.request_post(
            url=URL,
            params=[uid],
            data={'value': self.sample_normal['value']})
        self.assertEqual(response.status_code, 200, 'Post failed')

        response = Helpers.request_delete(
            url=URL,
            params=[uid])

        self.assertEqual(response.status_code, 200, 'Delete failed')

    def test_delete_exists(self):
        uid = self.new_uid()
        response = Helpers.request_post(
            url=URL,
            params=[uid],
            data={'value': self.sample_normal['value']})

        self.assertEqual(response.status_code, 200)

        response = Helpers.request_delete(
            url=URL,
            params=[uid])

        self.assertEqual(response.status_code, 200)

    def test_put_exists(self):
        first_content = self.sample_fixed['value']
        second_content = 'New content.'

        response = Helpers.request_post(
            url=URL,
            params=[self.sample_fixed['uid']],
            data={'value': first_content})

        self.assertEqual(response.status_code, 200, 'First post failed')

        first_len = len(response.content)
        difference = len(second_content) - len(first_content)
        expected_second_len = first_len + difference

        response = Helpers.request_put(
            url=URL,
            params=[self.sample_fixed['uid']],
            data={'value': 'New content.'})

        self.assertEqual(response.status_code, 200, 'Put failed')

        second_len = len(response.content)

        second_len -= 1     # Due to optional negative sign on check_sum

        self.assertLessEqual(second_len, expected_second_len)

        response = Helpers.request_delete(
            url=URL,
            params=[self.sample_fixed['uid']])

        self.assertEqual(response.status_code, 200, 'Delete failed')

 
if __name__ == '__main__':
    unittest2.main()
