from tastypie.resources import NamespacedModelResource
from tastypie.fields import ToManyField, ForeignKey

from clubm8core import models


class TagResource(NamespacedModelResource):
    class Meta:
        queryset = models.Tag.objects.all()
        resource_name = 'tag'


class EventResource(NamespacedModelResource):
    tags = ToManyField(TagResource, 'tag')

    class Meta:
        queryset = models.Event.objects.all()
        resource_name = 'event'


class OccurenceResource(NamespacedModelResource):
    event = ForeignKey(EventResource, 'event')

    class Meta:
        queryset = models.Occurrence.objects.all()
        resource_name = 'occurence'


class SpecialOccurenceResource(NamespacedModelResource):
    event = ForeignKey(EventResource, 'event')

    class Meta:
        queryset = models.SpecialOccurrence.objects.all()
        resource_name = 'special'


class PlanResource(NamespacedModelResource):
    occurrences = ToManyField(OccurenceResource, 'occurence')

    class Meta:
        queryset = models.Plan.objects.all()
        resources = 'plan'


class SlotResource(NamespacedModelResource):
    class Meta:
        slot = models.Slot.objects.all()
        resource_name = 'slot'
