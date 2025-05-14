# your_app/urls.py
from django.urls import path
from .views import EventCreateView,UserEventListView # 导入你的类视图

app_name = 'event'

urlpatterns = [
    path('events/create/', EventCreateView.as_view(), name='event_create'),

    # 用户事件列表页
    path('events/<str:username>/', UserEventListView.as_view(), name='user_events'),

]

 # 新增：创建事件的路由
    # 通常创建事件的 URL 是 /events/create/ 或 /users/<username>/events/create/
    # 如果是当前登录用户为自己创建事件，/events/create/ 更常见且简单
    # 如果需要在 URL 中体现用户名，并且假定只有 URL 中的用户才能创建（或者管理员为指定用户创建）
    # 考虑到 form_valid 中将 user 设置为 self.request.user，路由不带 username 更符合逻辑
    # 如果你坚持要在 URL 中带用户名，并假设只有 URL 中的用户名本人才能访问此创建页面（尽管创建的user还是request.user），
    # 并且这个username不用于指定创建者而是用于页面显示或 context，路由可以是：
    # path('users/<str:username>/events/create/', EventCreateView.as_view(), name='user_event_create'),
    # 但这与 form_valid 中的 user = self.request.user 逻辑冲突，需要调整视图
    # 暂定使用更简洁的 /events/create/ 路由