from django.conf.urls import url
from twittering import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'), # Notice the URL has been named
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^tweeting/$', views.tweeting, name='tweeting'),
]