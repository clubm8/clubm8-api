from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class NewsResourceTest(ResourceTestCaseMixin, TestCase):
    fixtures = ['clubm8core/news', 'clubm8core/test_user']

    def setUp(self):
        super(NewsResourceTest, self).setUp()

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/news/', format='json')
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 3)

    def test_get_list_filtered_from_before_first(self):
        params = {
            'since': '2015-01-01',
        }
        resp = self.api_client.get('/api/v1/news/', format='json',
                                   data=params)
        self.assertValidJSONResponse(resp)

        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 3)

        self.assertEqual(str(objects[0]['date']), '2016-09-17')
        self.assertEqual(str(objects[1]['date']), '2016-08-15')
        self.assertEqual(str(objects[2]['date']), '2016-08-02')

        for idx in range(0, 3):
            self.assertKeys(objects[idx], [
                'author',
                'date',
                'id',
                'text',
                'time',
                'title',
                'resource_uri',
            ])

    def test_get_list_filtered_from_after_first(self):
        params = {
            'since': '2016-08-03',
        }
        resp = self.api_client.get('/api/v1/news/', format='json',
                                   data=params)
        self.assertValidJSONResponse(resp)

        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 2)

        self.assertEqual(str(objects[0]['date']), '2016-09-17')
        self.assertEqual(str(objects[1]['date']), '2016-08-15')

    def test_get_list_filtered_from_after_last(self):
        params = {
            'since': '2017-01-01',
        }
        resp = self.api_client.get('/api/v1/news/', format='json',
                                   data=params)
        self.assertValidJSONResponse(resp)

        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 0)

    def test_get_list_filtered_until_after_last(self):
        params = {
            'until': '2017-01-01',
        }
        resp = self.api_client.get('/api/v1/news/', format='json',
                                   data=params)
        self.assertValidJSONResponse(resp)

        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 3)

        self.assertEqual(str(objects[0]['date']), '2016-09-17')
        self.assertEqual(str(objects[1]['date']), '2016-08-15')
        self.assertEqual(str(objects[2]['date']), '2016-08-02')

    def test_get_list_filtered_until_before_last(self):
        params = {
            'until': '2016-09-16',
        }
        resp = self.api_client.get('/api/v1/news/', format='json',
                                   data=params)
        self.assertValidJSONResponse(resp)

        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 2)

        self.assertEqual(str(objects[0]['date']), '2016-08-15')
        self.assertEqual(str(objects[1]['date']), '2016-08-02')

    def test_get_list_filtered_until_before_first(self):
        params = {
            'until': '2015-01-01',
        }
        resp = self.api_client.get('/api/v1/news/', format='json',
                                   data=params)
        self.assertValidJSONResponse(resp)

        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 0)

    def test_get_list_filtered_since_until_middle(self):
        params = {
            'since': '2016-08-03',
            'until': '2016-09-16',
        }
        resp = self.api_client.get('/api/v1/news/', format='json',
                                   data=params)
        self.assertValidJSONResponse(resp)

        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 1)

        self.assertEqual(str(objects[0]['date']), '2016-08-15')

    def test_get_details_fields(self):
        resp = self.api_client.get('/api/v1/news/1/', format='json')
        news = self.deserialize(resp)

        self.assertKeys(news, [
            'author',
            'date',
            'id',
            'text',
            'time',
            'title',
            'resource_uri',
        ])
