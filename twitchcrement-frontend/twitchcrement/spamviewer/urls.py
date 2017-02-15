from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.spamviewer_index, name='spamviewer_index'),
    url(r'^user/(\w+)/$', views.twitch_user_page),
    url(r'^spam/(\w+)/$', views.twitch_user_spam),
    url(r'^chat/(\w+)/$', views.twitch_user_chat)    
]
