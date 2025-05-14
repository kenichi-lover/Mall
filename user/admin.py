# accounts/admin.py
from django.contrib import admin
# 导入 Django 内置的 UserAdmin 类
from django.contrib.auth.admin import UserAdmin
# 导入你的自定义 MyUser 模型
from .models import MyUser

# 创建一个针对 MyUser 模型的自定义 Admin 类
# 继承自 Django 内置的 UserAdmin
class MyUserAdmin(UserAdmin):
    # 定义在 Admin 后台用户列表页面显示哪些字段
    # UserAdmin.list_display 包含了 Django 内置的默认字段 (如 username, email, is_staff 等)
    list_display = UserAdmin.list_display + ('name', 'telephone', 'is_seller')

    # 定义在 Admin 后台用户列表页面可以通过哪些字段进行过滤
    # UserAdmin.list_filter 包含了 Django 内置的默认过滤器 (如 is_staff, is_superuser, groups 等)
    list_filter = UserAdmin.list_filter + ('is_seller',) # 添加按 is_seller 过滤

    # 定义在 Admin 后台用户列表页面可以通过哪些字段进行搜索
    # UserAdmin.search_fields 包含了 Django 内置的默认搜索字段 (如 username, first_name, last_name, email)
    search_fields = UserAdmin.search_fields + ('name', 'telephone') # 添加按 name 和 telephone 搜索

    # 定义在 Admin 后台用户对象的“更改”表单页面显示的字段集和布局
    # UserAdmin.fieldsets 包含了 Django 内置的默认字段集
    # 我们在这里添加一个 'Custom Fields' 的新字段集来包含我们自定义的字段
    fieldsets = UserAdmin.fieldsets + (
        ('自定义字段', {'fields': ('name', 'telephone', 'is_seller')}),
    )

    # 定义在 Admin 后台“添加用户”表单页面显示的字段集和布局
    # UserAdmin.add_fieldsets 包含了 Django 内置的默认字段集
    # 在添加用户时，通常需要输入用户名和密码，所以这里的字段集会和更改表单略有不同
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('自定义字段', {'fields': ('name', 'telephone', 'is_seller')}),
    )

    # 可选：定义在 Admin 后台用户列表页面的默认排序方式
    # ordering = ('username',) # 默认通常是按 username 排序

# 将你的自定义 MyUser 模型与上面定义的 MyUserAdmin 类一起注册到 Admin 后台
admin.site.register(MyUser, MyUserAdmin)

# 如果你的 MyUser 模型没有添加任何自定义字段，或者你不需要在 Admin 中特殊处理它们
# 你也可以直接使用下面的简单注册方式，但通常推荐使用继承 UserAdmin 的方式
# admin.site.register(MyUser)
