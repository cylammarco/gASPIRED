from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
    url('aptrace', views.aptrace),
]