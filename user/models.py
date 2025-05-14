from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class MyUser(AbstractUser):
    name = models.CharField(verbose_name='用户',max_length=100,blank=True)
    telephone = models.CharField(verbose_name='电话号码',max_length=11,blank=True,default='暂时没有')
    is_seller = models.BooleanField(default=False, verbose_name="是否卖家")

    def __str__(self):
        return f"name: {self.name},telephone: {self.telephone}"
    
    class Meta:
        db_table = 'myuser'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

