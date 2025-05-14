# 在你的 urls.py 文件中

from django.urls import path
from .views import EmailFormView

app_name = 'myemail'

urlpatterns = [
 
    # 定义邮件发送表单页面的 URL 路由，使用 EmailFormView 的 as_view() 方法
    path('send-email/', EmailFormView.as_view(), name='send_email'),

]