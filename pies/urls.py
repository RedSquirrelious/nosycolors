from django.conf.urls import url, handler400, handler403, handler404, handler500
from pies import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'), # Notice the URL has been named
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^404/$', views.my404View.as_view(), name='404'),
    url(r'^pie_data/$', views.pie_data, name='pie_data'),
    url(r'^test_pie/$', views.test_pie, name='test_pie'),
    url(r'^hash_pie/$', views.hash_pie, name='hash_pie'),
]

handler400 = views.bad_request
