from tastypie import resources

from clubm8core import models


class EventResource(resources.ModelResource):
    class Meta:
        queryset = models.Event.objects.all()
        resource_name = 'event'
