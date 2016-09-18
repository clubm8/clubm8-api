from ddt import ddt, data
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin

FILTER_DATA = [
    {
        'valid': True,
        'filter': {
            'from': '2015-01-01',
        },
        'expected': {
            'count': 8,
        },
    },
    {
        'valid': True,
        'filter': {
            'from': '2016-10-30',
        },
        'expected': {
            'count': 1,
        },
    },
    {
        'valid': False,
        'filter': {
            'from': 'invalid',
        },
    },
    {
        'valid': True,
        'filter': {
            'to': '2017-01-01',
        },
        'expected': {
            'count': 8,
        },
    },
    {
        'valid': True,
        'filter': {
            'to': '2016-08-29',
        },
        'expected': {
            'count': 1,
        },
    },
    {
        'valid': False,
        'filter': {
            'to': 'invalid',
        },
    },
    {
        'valid': True,
        'filter': {
            'from': '2016-09-12',
            'to': '2016-10-23',
        },
        'expected': {
            'count': 5,
        },
    },
    {
        'valid': True,
        'filter': {
            'to': '2016-09-12',
            'from': '2016-10-23',
        },
        'expected': {
            'count': 0,
        },
    },
    {
        'valid': False,
        'filter': {
            'from': 'invalid',
            'to': '2016-10-23',
        },
    },
    {
        'valid': False,
        'filter': {
            'from': '2016-09-12',
            'to': 'invalid',
        },
    },
    {
        'valid': True,
        'filter': {
            'tags': ','.join(map(str, range(1, 26))),
        },
        'expected': {
            'count': 8,
        }
    },
    {
        'valid': True,
        'filter': {
            'tags': '1',
        },
        'expected': {
            'count': 6,
        }
    },
    {
        'valid': False,
        'filter': {
            'tags': 'invalid',
        },
    },
    {
        'valid': True,
        'filter': {
            'tags': '1',
            'from': '2016-09-30',
        },
        'expected': {
            'count': 2,
        }
    },
]


@ddt
class SlotResourceTest(ResourceTestCaseMixin, TestCase):
    fixtures = [
        'clubm8core/events',
        'clubm8core/occurrences',
        'clubm8core/plans',
        'clubm8core/slots',
        'clubm8core/tags',
        'clubm8core/test_user'
    ]

    def setUp(self):
        super(SlotResourceTest, self).setUp()

    def test_get_list_json(self):
        response = self.api_client.get(
            uri='/api/v1/slot/',
            data=None,
            format='json'
        )

        self.assertValidJSONResponse(response)

        objects = self.deserialize(response)['objects']
        self.assertEqual(len(objects), 8)

        self.assertKeys(objects[0], [
            'id',
            'plan',
            'resource_uri',
            'start',
        ])

    @data(*FILTER_DATA)
    def test_get_list_filter(self, value):
        response = self.api_client.get(
            uri='/api/v1/slot/',
            data=value['filter'],
            format='json'
        )

        if value['valid']:
            self.assertValidJSONResponse(response)
            self.assertEqual(
                len(self.deserialize(response)['objects']),
                value['expected']['count']
            )
        else:
            self.assertHttpBadRequest(response)
