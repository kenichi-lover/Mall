from django.db import models
from django.utils import timezone # 导入 timezone 用于时间戳字段
from django.conf import settings
# Create your models here.


# 如果你的商品需要关联分类，需要先定义一个 Category 模型
# from .category import Category # 假设你在 models.py 同级或其他地方定义了 Category 模型

class Product(models.Model):
    # CharField 用于短文本，通常用于名称
    name = models.CharField(
        max_length=255, # 最大长度
        verbose_name="商品名称", # 在 Admin 后台或表单中显示的更友好的名称
        help_text="输入商品的完整名称" # 在 Admin 后台或表单中显示的帮助文本
    )

    # TextField 用于长文本，适合商品描述
    description = models.TextField(
        blank=True, # 允许在表单中为空
        null=True,  # 允许在数据库中存储 NULL 值
        verbose_name="商品描述",
        help_text="输入商品的详细描述"
    )

    # DecimalField 用于精确的小数，适合表示货币金额
    price = models.DecimalField(
        max_digits=10,      # 总位数（包括小数点前后）例如：最大可以到 9,999,999.99
        decimal_places=2,   # 小数点后的位数
        verbose_name="商品价格",
        help_text="输入商品的销售价格 (例如: 19.99)"
    )

    # PositiveIntegerField 用于非负整数，适合表示库存数量
    stock = models.PositiveIntegerField(
        default=0, # 默认库存为 0
        verbose_name="库存数量",
        help_text="商品的当前库存量"
    )

    # BooleanField 用于布尔值，表示商品是否可购买/在售
    is_available = models.BooleanField(
        default=True, # 默认为在售
        verbose_name="是否在售",
        help_text="勾选表示商品当前正在销售"
    )

    # DateTimeField 用于存储日期和时间
    # auto_now_add=True 会在对象第一次创建时自动设置为当前时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    # auto_now=True 会在对象每次保存时自动更新为当前时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    # --- 可选字段 ---

    # ForeignKey 用于建立与其他模型的关联，例如商品分类
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # 关联到 MyUser 模型
        on_delete=models.CASCADE, # 当关联的 MyUser  被删除时，将此字段设为 NULL
        null=True,  # 允许商品没有分类
        blank=True, # 允许在表单中不选择分类
        related_name='products', # 在 MyUser  对象上反向查询关联 Product 时使用的名称 (例如: MyUser.products.all())
        verbose_name="所属用户",
        help_text="商品所属的用户或卖家"
    )

    # ImageField 用于上传图片文件
    # 需要安装 Pillow 库 (pip install Pillow) 并且在 settings.py 中配置 MEDIA_ROOT 和 MEDIA_URL
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/', # 图片上传到 MEDIA_ROOT 下的子目录，按年/月/日组织
        blank=True, # 允许为空
        null=True,  # 允许为 NULL
        verbose_name="商品图片",
    )

    def __str__(self):
        # 定义对象的字符串表示，在 Admin 网站和 Shell 中显示时很有用
            return f"name:{self.name},user:{self.user}"
    
    class Meta:
        # 先按用户排序，然后同一用户内的商品按名称排序
        ordering = ['user','name']
        # 可选：在 Admin 网站中显示的模型名称
        verbose_name = "商品"
        verbose_name_plural = "商品列表" # 复数形式的名称

        

    