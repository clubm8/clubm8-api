from tastypie.api import NamespacedApi
from clubm8api.api import (EventResource,
                           NewsResource,
                           PlanResource,
                           OccurenceResource,
                           SlotResource,
                           SpecialOccurenceResource,
                           TagResource,
                           )

app_name = 'clubm8api'

api = NamespacedApi(api_name='v1', urlconf_namespace=app_name)
api.register(EventResource())
api.register(NewsResource())
api.register(PlanResource())
api.register(OccurenceResource())
api.register(SlotResource())
api.register(SpecialOccurenceResource())
api.register(TagResource())

urlpatterns = api.urls
