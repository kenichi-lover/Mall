from django.shortcuts import redirect,render
from django.views.generic import View
from django.contrib.auth.views import LogoutView
from .forms import MyAuthenticationForm, RegisterForm
from django.contrib.auth import login, authenticate
from product.models import Product
from django.contrib import messages
import logging

# 推荐导入 reverse_lazy 来根据 URL 名称构建 URL
from django.urls import reverse_lazy

logger = logging.getLogger(__name__) # 获取 logger 实例，用于替代 print

class HomePageView(View):
    template_name = "home.html"
    success_url = reverse_lazy("home") # 登录/注册成功后重定向到首页

    def get_context_data(self, **kwargs):
        """
        准备所有渲染模板所需的上下文数据。
        这会在 get 和 post 方法中被调用。
        """
        context = {}

        # 1. 初始化表单
        # 只有当表单通过 POST 提交且验证失败时，才使用传入的表单实例
        # 否则，默认初始化新的空表单
        context["login_form"] = kwargs.get("login_form", MyAuthenticationForm())
        context["register_form"] = kwargs.get("register_form", RegisterForm())

        # 2. 控制模态框的显示和激活的 Tab
        # 这些值通常在 POST 请求处理失败后被设置为 True/特定 Tab
        context["show_modal_on_load"] = kwargs.get("show_modal_on_load", False)
        context["active_tab"] = kwargs.get("active_tab", "login-pane") # 默认激活登录Tab

        # 3. 获取卖家和商品数据 (与你原有的逻辑相同，但现在放在这里)
        # 特别留意。因为home模板新品展示区用到了seller1.name，在后台一定要填写name字段。不然，不会显示姓名，商品图片都不会展示。
        seller1 = None
        seller2 = None
        seller1_products = []
        seller2_products = []
        sellers_found = []# 用于存储找到的符合条件的卖家对象
        

        try:
            # 优化点 1：更高效地查找最近活跃的两个不同卖家
            # 使用 distinct() 需要在 order_by 之后，并且确保 user 字段可以被 distinct
            # 这里的逻辑是先获取最近的商品，再从中提取不重复的卖家
            recent_products_with_sellers = Product.objects.filter(
                is_available=True,
                user__isnull=False
            ).order_by("-created_at").select_related('user')[:20] # select_related 优化查询

            logger.debug("--- Debugging recent_products_with_sellers ---")
            for product in recent_products_with_sellers:
                logger.debug(f"Product ID: {product.id}, Name: {product.name}, Created At: {product.created_at}, Seller: {product.user.username if product.user else 'No User'}")
            logger.debug("--- End of recent_products_with_sellers Debug ---")

            for product in recent_products_with_sellers:
                if product.user and product.user not in sellers_found:
                    sellers_found.append(product.user)
                    if len(sellers_found) == 2:
                        break

            if len(sellers_found) > 0:
                seller1 = sellers_found[0]
                seller1_products = Product.objects.filter(
                    is_available=True,
                    user=seller1
                ).order_by("-created_at")[:4]

            if len(sellers_found) > 1:
                seller2 = sellers_found[1]
                seller2_products = Product.objects.filter(
                    is_available=True,
                    user=seller2
                ).order_by("-created_at")[:4]

            context["seller1"] = seller1
            context["seller1_products"] = list(seller1_products) # 转换为列表
            context["seller2"] = seller2
            context["seller2_products"] = list(seller2_products) # 转换为列表

            # 调试日志使用 logger
            logger.debug(f"HomePageView - Seller 1: {seller1.username if seller1 else 'None'}") # 假设用户模型有 username 属性
            logger.debug(f"HomePageView - Seller 1 Products Count: {len(seller1_products)}")
            logger.debug(f"HomePageView - Seller 2: {seller2.username if seller2 else 'None'}")
            logger.debug(f"HomePageView - Seller 2 Products Count: {len(seller2_products)}")

        except Exception as e:
            logger.error(f"Error fetching homepage products: {e}", exc_info=True) # 记录完整错误信息
            context["seller1"] = None
            context["seller1_products"] = []
            context["seller2"] = None
            context["seller2_products"] = []

        return context

    def get(self, request, *args, **kwargs):
        # 优化点 2：移除已登录用户的无限重定向。
        # 如果首页对已登录用户也可见，就不在这里重定向。
        # 否则，如果已登录用户访问首页应该被重定向到其他页面（如仪表盘），
        # 则在此处添加重定向逻辑：
        # if self.request.user.is_authenticated:
        #     return redirect(reverse_lazy('dashboard')) # 示例重定向到仪表盘
        # else:
        #     pass # 继续渲染首页

        context = self.get_context_data(request=request) # 确保 request 传递给 get_context_data 以便在内部判断用户状态
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request=request) # 获取基础上下文，包括商品数据等

        # 优化点 3：处理已登录用户提交表单的情况
        if self.request.user.is_authenticated:
            messages.info(request, "您已登录，无需再次登录或注册。")
            return redirect(self.success_url) # 已经登录了，直接重定向回首页

        # 区分是登录表单提交还是注册表单提交
        if 'login_submit' in request.POST:
            login_form = MyAuthenticationForm(request, data=request.POST)
            context['login_form'] = login_form # 更新上下文中的登录表单实例

            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "登录成功！")
                    return redirect(self.success_url)
                else:
                    messages.error(request, "无效的用户名或密码。")
                    context['show_modal_on_load'] = True
                    context['active_tab'] = 'login-pane'
            else:
                for field, errors in login_form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{login_form.fields[field].label}: {error}")
                context['show_modal_on_load'] = True
                context['active_tab'] = 'login-pane'

        elif 'register_submit' in request.POST:
            register_form = RegisterForm(request.POST)
            context['register_form'] = register_form # 更新上下文中的注册表单实例

            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                messages.success(request, "注册成功！您已自动登录。")
                return redirect(self.success_url)
            else:
                for field, errors in register_form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{register_form.fields[field].label}: {error}")
                context['show_modal_on_load'] = True
                context['active_tab'] = 'register-pane'
        else:
            messages.warning(request, "未知的表单提交。")
            # 如果是未识别的POST，也应渲染页面，而不是直接重定向，以便显示警告
            return render(request, self.template_name, context)

        # 如果 POST 请求未能成功重定向（例如表单验证失败），则重新渲染页面并显示错误
        return render(request, self.template_name, context)


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("home")
