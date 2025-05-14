from django.contrib import admin
from .models import Order # 从当前应用的 models.py 导入 Order 模型

# 注册 Order 模型到 Django 后台
# 基本注册方式
# admin.site.register(Order)

# 或者，为了在后台显示更多字段和提供搜索、过滤功能，可以创建一个 ModelAdmin 类
class OrderAdmin(admin.ModelAdmin):
    # 在列表页显示的字段
    list_display = ('order_id', 'user', 'product', 'quantity', 'total_price', 'status', 'created_at', 'paid_at')

    # 可以点击进入详情页的字段
    list_display_links = ('order_id',)

    # 可以在列表页直接编辑的字段
    # list_editable = ('status',) # 如果允许在列表页直接修改状态，可以添加这个

    # 用于过滤的字段（右侧边栏会出现过滤选项）
    list_filter = ('status', 'created_at', 'payment_method')

    # 用于搜索的字段（顶部会出现搜索框）
    search_fields = ('order_id', 'user__username', 'product__name', 'transaction_id') # user__username 表示搜索关联User模型的username字段

    # 按日期分层导航
    date_hierarchy = 'created_at'

    # 在详情页的字段分组
    fieldsets = (
        (None, { # 第一个分组，没有标题
            'fields': ('order_id', 'user', 'product', 'quantity', 'price_at_purchase', 'total_price', 'status')
        }),
        ('支付信息', { # 第二个分组，标题为“支付信息”
            'fields': ('payment_method', 'transaction_id', 'paid_at'),
            'classes': ('collapse',) # 可以选择是否折叠这个分组
        }),
        ('时间戳', { # 第三个分组
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # 可以选择是否折叠这个分组
        }),
    )

    # 设置某些字段为只读
    readonly_fields = ('order_id', 'created_at', 'updated_at', 'price_at_purchase', 'total_price') # 订单号、创建时间、更新时间、购买时单价、总价通常不应手动修改

    # 在添加或修改页面关联模型的显示方式，这里以user为例，可以用 RawId 或 Select
    # raw_id_fields = ('user', 'product') # 如果用户或产品很多，可以用ID输入框更高效

    # 如果你的 Order 模型使用了 OrderItem（一对多关系），可以在 Order 的详情页显示 OrderItem
    # from .models import OrderItem # 假设你有一个 OrderItem 模型
    # class OrderItemInline(admin.TabularInline): # StackedInline 或 TabularInline
    #     model = OrderItem
    #     extra = 0 # 默认显示0个额外的表单

    # inlines = [OrderItemInline] # 将 OrderItemInline 添加到 OrderAdmin 中


# 使用自定义的 OrderAdmin 类注册 Order 模型
admin.site.register(Order,OrderAdmin)