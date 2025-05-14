# your_app/views.py
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.contrib.auth import get_user_model # 推荐使用 get_user_model()
from .models import Event # 导入你的 Event 模型
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import EventForm
from django.urls import reverse_lazy

MyUser = get_user_model()

class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    # fields = ['name', 'description', 'price', 'stock', 'is_available'] # 或使用 form_class = ProductForm
    form_class = EventForm
    template_name = 'event/event_create.html' # 创建/修改共用表单模板

    # test_func 方法定义了权限测试
    def test_func(self):
        # 只有是卖家 (is_seller=True) 的用户才能通过测试
        # 确保 request.user 是 MyUser 实例，因为它继承自 AbstractUser，默认就有 is_authenticated 和 is_staff
        return self.request.user.is_authenticated and self.request.user.is_seller
        # 如果使用用户组：
        # return self.request.user.is_authenticated and self.request.user.groups.filter(name='卖家').exists()


    # form_valid 在表单验证通过后调用，用于保存对象
    def form_valid(self, form):
        # 在保存前，将当前登录的用户设置为商品的 user 字段
        form.instance.user = self.request.user
        # 调用父类的 form_valid 方法保存对象
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        在表单验证通过并对象保存成功后，动态生成重定向 URL
        """
        # 在这里，self.request 和 self.object (刚刚保存的 Event 实例) 都是可用的
        # 重定向到该用户（当前登录用户）的事件列表
        # 假设你的 user_event_list URL 名称是 'your_app:user_event_list'
        # 需要传递 username 参数，这里使用当前用户的 username
        return reverse_lazy('event:user_events', kwargs={'username': self.request.user.username})

class UserEventListView(ListView): # <-- 没有任何权限相关的 Mixin
    """
    显示某个用户创建的所有事件列表
    URL 模式: /events/<str:username>/
    任何用户都可以访问。
    """
    model = Event # 指定要查询的模型
    template_name = 'event/user_event_list.html' # 指定模板文件
    context_object_name = 'events' # 在模板中使用的变量名

    # 重新添加 get_queryset 方法来过滤事件
    def get_queryset(self):
        """
        根据 URL 中的 username 参数过滤事件
        """
        # 从 URL 参数中获取用户名
        username = self.kwargs['username']

        # 根据用户名查找用户，如果用户不存在则返回 404
        self.target_user = get_object_or_404(MyUser, username=username) # 将用户对象保存在实例属性中，方便 get_context_data 使用

        # 过滤出该用户创建的所有 Event 对象
        # 使用模型 Meta 中定义的 ordering
        return Event.objects.filter(user=self.target_user).order_by(*self.model._meta.ordering)

    # 重新添加 get_context_data 方法来将目标用户传递到模板
    def get_context_data(self, **kwargs):
        """
        在上下文中添加目标用户对象
        """
        context = super().get_context_data(**kwargs)
        # 将在 get_queryset 中找到的目标用户添加到上下文
        context['target_user'] = self.target_user
        return context
