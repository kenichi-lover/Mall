from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('list/',views.ProductListView.as_view(),name='list'),
    path('detail/<int:pk>/',views.ProductDetailView.as_view(),name='detail'),
    path('create/',views.ProductCreateView.as_view(),name='create'),
    path('update/',views.ProductUpdateView.as_view(),name='update'),
    path('delete/',views.ProductDeleteView.as_view(),name='delete'),
]
