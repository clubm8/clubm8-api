from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.http import HttpResponseGone, HttpResponseBadRequest
from django.utils.dateparse import parse_date
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.fields import ToManyField, ForeignKey, CharField
from tastypie.resources import NamespacedModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from datetime import datetime, timedelta

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
    """The SlotResource provides a list of slots as well as details of a
    single slot entry.

    Filtering criteria:
        limit (int): The maximum number of slots to deliver
        from (date): The start date of the first entry to deliver
        to (date): The start date of the last entry to deliver
        tags (list[int]): A set of tags that. An entry must have at least one
            of these tags to be included in the list.
    """

    plan = ForeignKey(PlanResource, 'plan')

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
            frm = parse_date(filters['from'])
            queryset = queryset & Q(start__gte=frm)

        if 'to' in filters:
            to = parse_date(filters['to'])
            queryset = queryset & Q(start__lte=to)

        if 'tags' in filters:
            tags = filters['tags'].split(',')
            queryset = queryset & Q(plan__occurence__event__tag__in=tags)

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

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>{})/current{}$'.format(
                self._meta.resource_name, trailing_slash()
            ), self.wrap_view('get_current'), name="api_get_current"),
        ]

    def get_current(self, request, **kwargs):
        today = datetime.now().date()
        week = today - timedelta(today.weekday())
        print(week)

        try:
            bundle = self.build_bundle(request=request)
            kwargs['from'] = str(week)
            kwargs['to'] = str(week)
            slot = self.cached_obj_get(
                bundle=bundle,
                **self.remove_api_resource_names(kwargs)
            )
        except ObjectDoesNotExist:
            return HttpResponseGone()
        except MultipleObjectsReturned:
            return HttpResponseBadRequest("More than one resource found.")

        data = self.full_dehydrate(self.build_bundle(obj=slot))
        return self.create_response(request=request, data=data)


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
