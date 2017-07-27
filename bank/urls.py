# encode: utf-8

from django.conf import settings
from django.conf.urls import include, url
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework.urlpatterns import format_suffix_patterns

from bank.views import *

router = routers.DefaultRouter(schema_title='Patient Mobile API')
router.register(r'conta', AccountViewSet, base_name='account')
router.register(r'caixa', ATMViewSet, base_name='atm')

schema_view = get_schema_view(title='Bank API')

urlpatterns = [
    url('^$', schema_view),
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += router.urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
