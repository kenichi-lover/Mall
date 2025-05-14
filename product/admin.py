from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    # 在列表页显示的字段
    list_display = ('name', 'price', 'stock', 'is_available', 'user', 'created_at')
    # 可以点击的字段，用于进入编辑页面
    list_display_links = ('name',)
    # 允许编辑的字段（直接在列表页编辑）
    list_editable = ('price', 'stock', 'is_available')
    # 搜索字段
    search_fields = ('name', 'description', 'user__username') # 可以搜索用户名（假设 User 模型有 username 字段）
    # 过滤器
    list_filter = ('is_available', 'created_at', 'user')
    # 排序方式（覆盖模型 Meta 中的 ordering）
    ordering = ('-created_at', 'name') # 先按创建时间倒序，再按名称正序

    # 在编辑页面显示的字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'image')
        }),
        ('价格与库存', {
            'fields': ('price', 'stock', 'is_available')
        }),
        ('关联信息', {
            'fields': ('user',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # 可折叠
        }),
    )

    # 设置只读字段
    readonly_fields = ('created_at', 'updated_at')

    # 可以添加一些自定义行为，例如保存时的操作
    # def save_model(self, request, obj, form, change):
    #     obj.modified_by = request.user
    #     super().save_model(request, obj, form, change)

admin.site.register(Product, ProductAdmin)