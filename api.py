from django.db.models import Q
from django.utils.dateparse import parse_date
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.fields import ToManyField, ForeignKey
from tastypie.resources import NamespacedModelResource, ALL, ALL_WITH_RELATIONS

from clubm8core import models


class Authentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
            return True
        return super(Authentication, self).is_authenticated(request, **kwargs)


class Authorization(DjangoAuthorization):
    def is_authorized(self, request, object=None):
        if request.method == 'GET':
            return True
        else:
            return super(Authorization, self).is_authorized(request, object)


class TagResource(NamespacedModelResource):
    class Meta:
        queryset = models.Tag.objects.all().distinct()
        resource_name = 'tag'


class EventResource(NamespacedModelResource):
    tags = ToManyField(TagResource, 'tag')

    class Meta:
        queryset = models.Event.objects.all().distinct()
        resource_name = 'event'
        filtering = {
            'tags': ALL,
        }


class OccurenceResource(NamespacedModelResource):
    event = ForeignKey(EventResource, 'event')

    class Meta:
        queryset = models.Occurrence.objects.all().distinct()
        resource_name = 'occurence'
        filtering = {
            'event': ALL_WITH_RELATIONS,
        }


class SpecialOccurenceResource(NamespacedModelResource):
    event = ForeignKey(EventResource, 'event')

    class Meta:
        queryset = models.SpecialOccurrence.objects.all().distinct()
        resource_name = 'special'
        filtering = {
            'event': ALL_WITH_RELATIONS,
        }


class PlanResource(NamespacedModelResource):
    occurences = ToManyField(OccurenceResource, 'occurence')

    class Meta:
        queryset = models.Plan.objects.all().distinct()
        resources_name = 'plan'
        filtering = {
            'occurences': ALL_WITH_RELATIONS,
        }


class SlotResource(NamespacedModelResource):
    class Meta:
        queryset = models.Slot.objects.all().distinct()
        resource_name = 'slot'

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(SlotResource, self).build_filters(filters)

        queryset = Q(id__gte=0)

        if 'from' in filters:
            frm = filters['from']
            queryset = queryset & Q(start__gte=parse_date(frm))

        if 'to' in filters:
            to = filters['to']
            queryset = queryset & Q(start__lte=parse_date(to))

        orm_filters.update({'custom': queryset})
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None

        prefiltered = super(SlotResource, self).apply_filters(request, applicable_filters)
        return prefiltered.filter(custom) if custom else prefiltered



class NewsResource(NamespacedModelResource):
    class Meta:
        queryset = models.News.objects.all().distinct()
        resource_name = 'news'
        filtering = {
            'date': ['exact', 'range'],
            'author': ALL,
        }

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(NewsResource, self).build_filters(filters)

        queryset = Q(id__gte=0)

        if 'since' in filters:
            since = filters['since']
            queryset = queryset & Q(date__gte=parse_date(since))

        if 'until' in filters:
            until = filters['until']
            queryset = queryset & Q(date__lte=parse_date(until))

        orm_filters.update({'custom': queryset})
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None

        prefiltered = super(NewsResource, self).apply_filters(request, applicable_filters)
        return prefiltered.filter(custom) if custom else prefiltered

