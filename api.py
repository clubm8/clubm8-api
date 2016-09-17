from django.db.models import Q
from django.utils.dateparse import parse_date
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.fields import ToManyField, ForeignKey, CharField
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

    def build_filters(self, filters=None, **kwargs):
        if filters is None:
            filters = {}

        orm_filters = super(PlanResource, self).build_filters(filters,
                                                              **kwargs)

        queryset = Q(id__gte=0)

        if 'tags' in filters:
            tags = filters['tags']
            queryset = queryset & Q(occurence__event__tag__in=tags.split(','))

        orm_filters.update({'custom': queryset})
        return orm_filters

    def apply_filters(self, request, filters):
        if 'custom' in filters:
            custom = filters.pop('custom')
        else:
            custom = None

        prefiltered = super(PlanResource, self).apply_filters(request,
                                                              filters)
        return prefiltered.filter(custom) if custom else prefiltered


class SlotResource(NamespacedModelResource):
    class Meta:
        queryset = models.Slot.objects.all().distinct()
        resource_name = 'slot'

    def build_filters(self, filters=None, **kwargs):
        if filters is None:
            filters = {}

        orm_filters = super(SlotResource, self).build_filters(filters,
                                                              **kwargs)

        queryset = Q(id__gte=0)

        if 'from' in filters:
            frm = filters['from']
            queryset = queryset & Q(start__gte=parse_date(frm))

        if 'to' in filters:
            to = filters['to']
            queryset = queryset & Q(start__lte=parse_date(to))

        orm_filters.update({'custom': queryset})
        return orm_filters

    def apply_filters(self, request, filters):
        if 'custom' in filters:
            custom = filters.pop('custom')
        else:
            custom = None

        prefiltered = super(SlotResource, self).apply_filters(request,
                                                              filters)
        return prefiltered.filter(custom) if custom else prefiltered


class NewsResource(NamespacedModelResource):
    """The NewsResource provides a list of news as well as details of a single
    news entry.

    Filtering criteria:
        limit (int): The maximum number of news to deliver
        since (date): The date of the first entry to deliver
        until (date): The date of the last entry to deliver
    """

    author = CharField(attribute='author__get_full_name', default='nobody')

    class Meta:
        queryset = models.News.objects.all().distinct()
        resource_name = 'news'

    def build_filters(self, filters=None, **kwargs):
        if filters is None:
            filters = {}

        orm_filters = super(NewsResource, self).build_filters(filters,
                                                              **kwargs)

        queryset = Q(id__gte=0)

        if 'since' in filters:
            since = filters['since']
            queryset = queryset & Q(date__gte=parse_date(since))

        if 'until' in filters:
            until = filters['until']
            queryset = queryset & Q(date__lte=parse_date(until))

        orm_filters.update({'custom': queryset})
        return orm_filters

    def apply_filters(self, request, filters):
        if 'custom' in filters:
            custom = filters.pop('custom')
        else:
            custom = None

        prefiltered = super(NewsResource, self).apply_filters(request,
                                                              filters)
        return prefiltered.filter(custom) if custom else prefiltered
