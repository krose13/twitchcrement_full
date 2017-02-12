from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='spamsearcher_index'),
    url(r'^results/$', views.search, name='spamsearcher_search')
]
