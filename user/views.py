from django.shortcuts import redirect
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import MyAuthenticationForm, RegisterForm
from django.contrib.auth import login
from django.views.generic import TemplateView
from product.models import Product

# 推荐导入 reverse_lazy 来根据 URL 名称构建 URL
from django.urls import reverse_lazy


class HomePageView(TemplateView):
    template_name = "home.html"

    # 重写 get_context_data 方法来添加额外的上下文
    def get_context_data(self, **kwargs):
        # 调用父类 (TemplateView) 的 get_context_data 方法，获取其提供的默认上下文
        context = super().get_context_data(**kwargs)

        # 向获取到的上下文字典中添加您的表单实例
        context["login_form"] = MyAuthenticationForm()
        context["register_form"] = RegisterForm()

        # 初始化要传递给模板的卖家和商品列表变量
        seller1 = None
        seller2 = None
        seller1_products = []
        seller2_products = []
        sellers_found = [] # 用于存储找到的符合条件的卖家对象

        try:
            # 1. 查找最近活跃的两个不同卖家
            # 获取近期发布的一些在售商品，按创建时间倒序排列
            # 我们获取多一点（例如20个）以便找到不同的卖家
            recent_available_products = Product.objects.filter(
                is_available=True, # 只看在售商品
                user__isnull=False # 确保商品有所属的卖家
            ).order_by("-created_at")[:20] # 取最近的20个商品来查找卖家

            # 遍历这些商品，找出不同的卖家，直到找到两个
            for product in recent_available_products:
                if product.user and product.user not in sellers_found:
                    sellers_found.append(product.user)
                    if len(sellers_found) == 2:
                        break # 已经找到两个不同的卖家了

            # 2. 如果找到了第一个卖家，获取他最新的 4 个商品
            if len(sellers_found) > 0:
                seller1 = sellers_found[0]
                seller1_products = Product.objects.filter(
                    is_available=True, # 在售
                    user=seller1 # 属于这个卖家
                ).order_by("-created_at")[:4] # 取他最新的 4 个商品

            # 3. 如果找到了第二个卖家，获取他最新的 4 个商品
            if len(sellers_found) > 1:
                seller2 = sellers_found[1]
                seller2_products = Product.objects.filter(
                    is_available=True, # 在售
                    user=seller2 # 属于这个卖家
                ).order_by("-created_at")[:4] # 取他最新的 4 个商品


            # *** 将获取到的卖家对象和他们的商品列表添加到上下文中 ***
            context["seller1"] = seller1
            # 将 QuerySet 转换为列表，有时在模板中处理更保险
            context["seller1_products"] = list(seller1_products)

            context["seller2"] = seller2
            context["seller2_products"] = list(seller2_products)


            # 添加调试打印，确认获取到的数据
            print(f"DEBUG: HomePageView - Seller 1: {seller1.name if seller1 else 'None'}")
            print(f"DEBUG: HomePageView - Seller 1 Products Count: {len(seller1_products)}")
            print(f"DEBUG: HomePageView - Seller 2: {seller2.name if seller2 else 'None'}")
            print(f"DEBUG: HomePageView - Seller 2 Products Count: {len(seller2_products)}")

        except Exception as e:
            print(f"Error fetching homepage products: {e}")
            # 如果发生错误，提供空的变量
            context["seller1"] = None
            context["seller1_products"] = []
            context["seller2"] = None
            context["seller2_products"] = []


        # 返回修改后的上下文字典
        return context


class RegisterView(CreateView):  # 实现注册功能
    template_name = "home.html"
    form_class = RegisterForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class MyLoginView(LoginView):
    # 指定用于显示登录表单的模板
    # （如果您的 home.html 包含模态框，这里可以指向 home.html)
    template_name = "home.html"

    # === 使用您的 MyAuthenticationForm (包含 widget 自定义) ===
    form_class = MyAuthenticationForm

    success_url = reverse_lazy("home")  # 设置您的成功跳转 URL

    # === 注意：在正常情况下，您不需要重写 post 或 get 方法 ===

    # 这是最标准的方法。在您的项目的 settings.py 文件中添加或修改 LOGIN_REDIRECT_URL 设置，
    # 将其值设置为您希望用户登录后跳转到的 URL 或 URL 名称。


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("home")
