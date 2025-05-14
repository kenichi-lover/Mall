from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from .models import MyUser


'''
ModelForm (以及基于它的 UserCreationForm): 用于与数据库模型进行交互，创建或更新模型实例。需要 Meta.model 来指定操作哪个模型。
'''

class RegisterForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请确认密码'
        })


'''
普通 Form (如 AuthenticationForm): 只用于收集和验证任意数据，不直接与数据库模型进行保存操作。不需要 Meta.model。
'''

class MyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            # 设置 HTML 元素的 class 属性为 form-control，这通常用于 Bootstrap 等 CSS 框架来应用样式。
             'class': 'form-control',
             'placeholder':'请输入用户名',
             'autocomplete':'username',
         })
        self.fields['password'].widget.attrs.update({
             'class': 'form-control',
             'placeholder':'请输入密码',
            # autocomplete 是 HTML5 的属性，用于告知浏览器是否应该为该输入字段提供自动完成的建议。
            # 'current_password' 是一个特定的值，指示浏览器这是一个当前密码字段，浏览器可能会提供与当前网站相关的已保存密码。
             'autocomplete':'current_password'
         })


   