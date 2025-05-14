from django.urls import path
from . import views

app_name = 'myblog'

urlpatterns = [
    path('', views.index_view, name='index'),
]