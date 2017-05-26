from .views import authorise, success
from django.conf.urls import url

urlpatterns = [
    url(r'^authorise/$', authorise, name='sage-api-authorise'),
    url(r'^success/$', success, name='sage-api-success'),
]
