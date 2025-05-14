from django.urls import path
from . import views
from django.views.generic import TemplateView
app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),

    #这里的 TemplateView.as_view(template_name='about.html') 就充当了视图的角色。不需要写视图类或函数。
    path('about/', TemplateView.as_view(template_name='user/about.html'), name='about'),
    path('about_ai/', TemplateView.as_view(template_name='user/about_ai.html'), name='about_ai'),
    path('about_secret/', TemplateView.as_view(template_name='user/about_secret.html'), name='about_secret'),
]
