from django.urls import path
from . import views

app_name = 'spotify'
urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('detail', views.detail, name='detail'),
]
