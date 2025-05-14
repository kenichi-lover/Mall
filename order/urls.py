from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    # POST请求，创建订单并返回订单号
    path('buy/<int:product_id>/', views.buy_now, name='buy_now'),

    # GET请求，显示支付确认页面
    # 使用 order_id_or_pk 以兼容 UUID 或 PK (视图中是按 order_id 查找)
    path('payment/<str:order_id_or_pk>/', views.payment_page, name='payment_page'),

    # POST请求，处理支付确认页面的表单提交，调用支付宝SDK并重定向
    path('payment/initiate/<str:order_id>/', views.payment_initiate, name='payment_initiate'),

    # 支付宝回调 (POST请求)
    path('alipay/notify/', views.alipay_notify_view, name='alipay_notify'),
    # 支付宝同步返回 (GET请求), 用于用户重定向
    path('alipay/return/', views.payment_return_view, name='payment_return'),

    # 订单详情页面 (GET请求)
    path('detail/<str:order_id_or_pk>/', views.order_detail_view, name='detail'),

    # 您可能还需要其他订单相关的路由，例如订单列表
    # path('list/', views.order_list_view, name='list'), # 如果您有订单列表视图
]