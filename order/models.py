from django.db import models
from django.conf import settings # For User model
from product.models import Product
import uuid 
# 唯一订单号 (order_id): 增加一个对用户更友好的、唯一的订单号字段（例如使用 uuid.uuid4 生成），而不是仅依赖数据库自增ID。这在与用户沟通或第三方系统对接时更方便。

# 将常量用于选择项是一种很好的做法。
class OrderStatus(models.TextChoices):
    UNPAID = '待支付'
    PAID = '已支付'
    CANCELED = '已取消'
    SHIPPED = '已发货' # Example of another status
    COMPLETED = '已完成' # Example

class Order(models.Model):
    # 使用 settings.AUTH_USER_MODEL 这种方式比直接导入要更灵活。
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    # 如果您想要一个类似购物车的系统，且每个订单包含多种商品，请考虑使用“OrderItem”模型。
    # 目前，假设每次订单只有一种产品类型：
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="商品") # “保护”功能：若订单存在，则防止删除产品。

    order_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4, editable=False, verbose_name="订单号") # 更易于使用的独特标识符
    quantity = models.PositiveIntegerField(default=1, verbose_name="购买数量")
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="购买时单价") # 将库存价格设为默认值，以防产品价格发生变化时使用。
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="总价")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="下单时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间") # 有助于跟踪状态变化

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.UNPAID,
        verbose_name="订单状态"
    )

    # Payment specific fields
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name="支付方式")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="支付交易号") # 来自支付宝等。
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="支付时间")

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单列表"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

    def calculate_total_price(self):
        # 确保在订单创建时，产品价格取自产品模型中的相应数值。
        # 或者，如果您为该商品记录了“购买时价格”这一信息
        if self.product:
            return self.product.price * self.quantity
        return 0

    def save(self, *args, **kwargs):
        # 如果尚未设置或需要重新计算，则在保存之前先计算出总价
        if not self.pk: # 如果有了新的指令/订单
            self.price_at_purchase = self.product.price # 保存当前产品价格
        self.total_price = self.price_at_purchase * self.quantity
        super().save(*args, **kwargs)

# 如果您每次下单需要多种商品（需要具备购物车功能）:
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.PROTECT) # Or SET_NULL if product can be deleted but order item remains
#     quantity = models.PositiveIntegerField(default=1)
#     price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2) # Price of the product when order was placed
#
#     def get_cost(self):
#         return self.price_at_purchase * self.quantity
#
#     def __str__(self):
#         return f"{self.quantity} of {self.product.name}"
#
# # 那么订单模型就不会直接包含“产品”和“数量”这两个要素了。
# # “总价格”将通过将订单项的成本相加来计算得出。


'''
要点：
记录购买时价格 (price_at_purchase): 这是一个非常重要的字段。商品价格可能会变动，订单中应保存用户下单那一刻的商品单价，以确保订单总价的准确性。
时间戳: 增加 updated_at 字段 (使用 auto_now=True)，用于追踪订单信息的最后更新时间。
payment_method (支付方式，如：alipay, wechat_pay)
transaction_id (支付网关返回的交易流水号)
paid_at (支付成功的时间)
on_delete=models.PROTECT: 防止在仍有订单关联某个商品时，该商品被意外删除。
考虑是否需要支持一个订单包含多种商品（购物车功能）。如果需要，应设计 OrderItem（订单项）模型，Order 模型则不直接关联 product 和 quantity。当前您的模型是一个订单对应一种商品。
'''