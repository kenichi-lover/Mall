
from django.contrib import admin
from django.urls import path,include
from user import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.HomePageView.as_view(),name='home'),
    path('user/',include('user.urls',namespace='user')),
    path('product/',include('product.urls',namespace='product')),
    path('myemail/',include('myemail.urls',namespace='myemail')),
    path('event/',include('event.urls',namespace='event')),
    path('order/',include('order.urls',namespace='order')),
    path('mycache/',include('mycache.urls',namespace='mycache')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)