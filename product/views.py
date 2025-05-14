# products/views.py
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
# 导入用于权限控制的 Mixins
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Product # 你的 Product 模型
from .forms import ProductForm
# from .forms import ProductForm # 你可能需要一个 Product 表单

# --- 商品列表视图 (买家和访客可以浏览) ---
class ProductListView(ListView):
    model = Product
    template_name = 'product/list.html' # 列表模板
    paginate_by = 3
    context_object_name = 'products'
    
    def get_queryset(self):
        """
        重写 get_queryset 方法，根据请求中的 'q' 参数过滤商品。
        """
        # 首先获取基础的查询集（所有在售商品）
        queryset = Product.objects.filter(is_available=True)

        # 从 GET 请求参数中获取搜索关键词 'q'
        query = self.request.GET.get('q')

        # 如果获取到了搜索关键词
        if query:
            # 使用 __icontains 过滤 queryset，查找商品名称中包含关键词的商品（不区分大小写）
            queryset = queryset.filter(name__icontains=query)
            # 如果你需要更复杂的搜索（例如同时搜索名称和描述），可以使用 Q 对象：
            # queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))


        # 按照商品名称排序（保持原有排序需求）
        queryset = queryset.order_by('name')

        return queryset

    # 可选：重写 get_context_data 方法，将搜索关键词添加到模板上下文中
    # 这有助于在 product/list.html 模板中预填充搜索框和处理分页链接
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 将搜索关键词添加到上下文中，模板中可以通过 {{ search_query }} 访问
        context['search_query'] = self.request.GET.get('q', '')
        # 确保分页器能正确处理带有搜索参数的 URL
        # 这部分处理通常在模板中通过在分页链接中包含 ?q={{ search_query }} 实现，
        # 但在 context 中提供 search_query 变量会更方便。
        return context
    

# --- 商品详情视图 (买家和访客可以浏览) ---
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/detail.html' # 详情模板
    context_object_name = 'product'
    # 可以选择覆盖 get_queryset 或 get_object 来确保只显示在售商品
    # def get_object(self, queryset=None):
    #     obj = super().get_object(queryset)
    #     # 允许站点管理员看到所有商品，普通用户只能看到在售的
    #     if not obj.is_available and not self.request.user.is_staff:
    #          raise Http404("商品不存在或已下架。") # 或返回一个友好的页面
    #     return obj
    


# --- 商品创建视图 (只允许卖家访问) ---
# LoginRequiredMixin: 要求用户必须登录
# UserPassesTestMixin: 检查用户是否通过了 test_func 定义的测试
class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    # fields = ['name', 'description', 'price', 'stock', 'is_available'] # 或使用 form_class = ProductForm
    form_class = ProductForm
    template_name = 'product/upload.html' # 创建/修改共用表单模板
    success_url = reverse_lazy('product:list') # 创建成功后跳转到商品列表

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
        # 可以在这里强制设置一些字段，比如刚创建的商品默认为在售
        form.instance.is_available = True
        return super().form_valid(form)

    


# --- 商品更新视图 (只允许商品所有者卖家访问) ---
class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    # fields = ['name', 'description', 'price', 'stock', 'is_available'] # 或使用 form_class = ProductForm
    form_class = ProductForm
    template_name = 'product/product:form.html' # 创建/修改共用表单模板

    # 获取成功跳转 URL，重定向到更新后的商品详情页
    def get_success_url(self):
        return reverse_lazy('product:detail', kwargs={'pk': self.object.pk})

    # test_func 方法定义权限测试
    # 只有是登录用户，并且当前登录用户是商品对象的 user 字段所关联的用户时才通过
    def test_func(self):
        product = self.get_object() # 获取当前要更新的 Product 对象
        # 确保用户已登录，并且用户是商品的所有者
        return self.request.user.is_authenticated and self.request.user == product.user

    # 可选：处理 test_func 失败的情况 (用户不是所有者)
    # def handle_no_permission(self):
    #    return redirect('permission_denied_page') # 或 raise Http403


# --- 商品删除视图 (只允许商品所有者卖家访问) ---
class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html' # 删除确认模板
    success_url = reverse_lazy('product:list') # 删除成功后跳转到商品列表

    # test_func 方法定义权限测试
    # 只有是登录用户，并且当前登录用户是商品对象的 user 字段所关联的用户时才通过
    def test_func(self):
        product = self.get_object() # 获取当前要删除的 Product 对象
        # 确保用户已登录，并且用户是商品的所有者
        return self.request.user.is_authenticated and self.request.user == product.user

    # 可选：处理 test_func 失败的情况
    # def handle_no_permission(self):
    #    return redirect('permission_denied_page') # 或 raise Http403