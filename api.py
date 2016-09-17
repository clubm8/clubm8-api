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
        resources = 'plan'
        filtering = {
            'occurences': ALL_WITH_RELATIONS,
        }


class SlotResource(NamespacedModelResource):
    class Meta:
        slot = models.Slot.objects.all().distinct()
        resource_name = 'slot'
