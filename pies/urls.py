from django.conf.urls import url
from pies import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'), # Notice the URL has been named
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^pie_data/$', views.pie_data, name='pie_data'),
    url(r'^test_pie/$', views.test_pie, name='test_pie'),
    url(r'^hash_pie/$', views.hash_pie, name='hash_pie'),
]