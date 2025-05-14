# 在你的应用的 forms.py 文件中

from django import forms

# 定义一个用于邮件发送的表单类
class EmailForm(forms.Form):
    email = forms.EmailField(
        label="请输入您的邮箱地址", # 表单字段的标签
        max_length=254, # 邮箱地址的标准最大长度
        # 使用 EmailInput widget，并添加 placeholder 属性
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        required=True # 设置字段为必填项
    )
    # 如果以后需要添加其他字段（如主题、邮件内容等），可以在这里添加
    # subject = forms.CharField(label="主题", max_length=100, required=False)
    # message = forms.CharField(label="邮件内容", widget=forms.Textarea, required=False)


'''
模型表单 (ModelForm) 的用途： 模型表单是 Django 提供的一种便捷方式，它可以根据您已有的 Django 模型自动生成表单字段。
模型表单的主要目的是用来方便地创建或更新模型实例的数据。当您提交并保存一个模型表单时，它会自动将表单数据映射到对应的模型字段，并保存到数据库中。

邮件发送表单的目的： 根据您之前明确的需求，您的邮件发送表单是让用户输入一个任意的邮箱地址，然后系统将邮件发送到这个地址。用户输入的这个邮箱地址是用来作为邮件的收件人，用于执行发送邮件的操作。

数据流向不同：

模型表单收集的数据是流向数据库，用于创建或更新一个模型对象。
您的邮件发送表单收集的邮箱地址是流向您的视图逻辑，用于作为 send_mail() 函数的一个参数。这个邮箱地址本身通常不会被用来创建或更新您的用户模型、商品模型或任何其他已有的模型实例。
总结：

因为您的邮件发送表单收集的数据（收件人邮箱地址）并不是用来直接创建或更新数据库中的某个模型实例的，所以使用模型表单 (ModelForm) 是不合适的。

您之前使用的标准表单 (forms.Form) 是正确的选择。
标准表单用于处理不直接与模型关联的任意数据，比如搜索表单、联系表单（如果数据不存入数据库）、或者像您这样的发送邮件表单，这些表单的数据用于执行某个操作或流程。
'''
