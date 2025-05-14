from django.db import models
from user.models import MyUser
from django.contrib.auth import get_user_model # 推荐使用 get_user_model()
# Create your models here.

MyUser = get_user_model() # 获取当前活跃的用户模型

class Event(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE,verbose_name='创建者')

    def __str__(self):
        # 更好的 __str__ 表示
        return f"Event: {self.title} by {self.user.username if self.user else 'N/A'}"

    class Meta:
        ordering = ['user','start_time']
        verbose_name = '活动'
        verbose_name_plural = verbose_name