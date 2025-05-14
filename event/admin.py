# event/admin.py
from django.contrib import admin
from .models import Event # 从当前应用的 models.py 导入 Event 模型

# 创建一个 ModelAdmin 类来定制 Event 在后台的显示
class EventAdmin(admin.ModelAdmin):
    # list_display: 在列表页面显示的字段
    list_display = ('title', 'user', 'start_time', 'end_time', 'location')

    # list_filter: 在列表页面右侧添加过滤选项
    list_filter = ('user', 'start_time', 'end_time')

    # search_fields: 在列表页面顶部添加搜索框，指定搜索的字段
    search_fields = ('title', 'description', 'location', 'user__username') # user__username 允许按用户名搜索

    # date_hierarchy: 在列表页面顶部添加日期导航，按日期进行筛选
    date_hierarchy = 'start_time' # 或 'end_time'

    # ordering: 默认的排序方式（优先级高于 Model Meta 中的 ordering）
    # ordering = ['-start_time']

    # raw_id_fields: 对于外键字段，如果关联对象很多，可以使用 raw_id_fields
    # 它会将下拉选择框变成一个输入框，需要手动输入关联对象的 ID，旁有一个放大镜按钮用于搜索
    raw_id_fields = ('user',) # 如果用户很多，推荐使用

    # fieldsets: 在编辑/创建页面对字段进行分组和布局
    # fieldsets = (
    #     (None, {
    #         'fields': ('title', 'description')
    #     }),
    #     ('时间和地点', {
    #         'fields': ('start_time', 'end_time', 'location'),
    #         'classes': ('collapse',), # 添加 collapse 可以让这个分组默认折叠起来
    #     }),
    #     ('关联信息', {
    #          'fields': ('user',),
    #     }),
    # )

    # readonly_fields: 设置只读字段，在编辑页面不能修改
    # 例如，如果 user 是在 form_valid 中自动设置的，你可能希望在编辑时它是只读的
    # readonly_fields = ('user',)

# 注册 Event 模型，并关联定制的 EventAdmin 类
admin.site.register(Event, EventAdmin)
