from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.spamviewer_index, name='spamviewer_index'),
	url(r'^(\w+)/$', views.twitch_user_page)
]
