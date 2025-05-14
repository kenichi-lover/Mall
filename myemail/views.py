# 在你的 views.py 文件中

from django.views.generic.edit import FormView # 导入 FormView
from .forms import EmailForm # 从当前应用的 forms.py 导入 EmailForm
from django.core.mail import send_mail # 导入 Django 的发送邮件函数
from django.conf import settings # 导入 settings
from django.urls import reverse_lazy # 导入 reverse_lazy，推荐用于 success_url
from django.contrib import messages # 可选：导入 messages 框架

# 使用 FormView 处理邮件发送表单
class EmailFormView(FormView):
    template_name = 'myemail/send_email.html' # 指定用于渲染表单的模板文件
    form_class = EmailForm # 指定使用哪个 Form 类
    # 表单成功提交并处理后重定向的 URL，使用 reverse_lazy 防止 URLConf 未加载时出错
    success_url = reverse_lazy('home') 

    # 当表单验证通过时，会自动调用这个方法
    def form_valid(self, form):
        """
        当表单数据有效时，执行邮件发送逻辑。
        """
        # 从经过清洗的表单数据中获取邮箱地址
        recipient_email = form.cleaned_data['email']

        try:
            # 定义邮件参数
            subject = '您的网站测试邮件' # 邮件主题
            message = f'您好，这是一封发送到 {recipient_email} 的测试邮件，通过 FormView 发送。' # 邮件正文
            from_email = settings.DEFAULT_FROM_EMAIL # 发件人邮箱
            recipient_list = [recipient_email] # 收件人列表

            # 发送邮件
            send_mail(subject, message, from_email, recipient_list)

            # 可选：添加成功消息
            messages.success(self.request, f'邮件已成功发送到 {recipient_email}！')

            # 调用父类的 form_valid 方法，它会处理重定向到 success_url
            return super().form_valid(form)

        except Exception as e:
            # 处理发送邮件过程中发生的错误
            # 可选：添加错误消息
            messages.error(self.request, f'发送邮件失败：{e}')
            # 将错误添加到表单的非字段错误中，以便在模板中显示
            form.add_error(None, f'发送邮件失败：{e}')
            # 返回 form_invalid 方法，它会重新渲染带有错误信息的表单模板
            return self.form_invalid(form)

    '''
    发送到用户在表单中填写的邮箱（例如 paulken731@gmail.com）的邮件，其内容应该是：

    主题 (Subject): '您的网站测试邮件'
    正文 (Body): '您好，这是一封发送到 paulken731@gmail.com 的测试邮件，通过 FormView 发送。' （其中的邮箱地址会替换为用户实际填写的地址）
    这封邮件是用来验证您的邮件发送功能是否能成功将邮件发送到指定的收件人地址。

    如果您希望发送的是其他内容，例如一个产品推广信息、活动通知或者简单的确认邮件，您只需要修改 myemail/views.py 文件中 subject 和 message 这两个变量的值即可。
    您甚至可以使用 Django 的模板系统来生成更复杂的 HTML 邮件内容。
    '''



