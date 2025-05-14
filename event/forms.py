from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # fields = '__all__' # 修正: 不要包含 'user' 字段，它在视图中自动设置
        fields = ['title', 'start_time', 'end_time', 'location', 'description'] # 明确列出需要用户填写的字段

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入活动标题'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入活动描述'}),
            # 修正3 & 4: start_time 和 end_time 是 DateTimeField，应该使用 DateTimeInput 或相关的日期时间选择器 widget
            # 默认的 DateTimeInput 渲染为文本输入，你可以根据需要集成 JS 库提供更好的日期时间选择体验
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}), # 使用 HTML5 input type datetime-local
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}), # 使用 HTML5 input type datetime-local
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入活动地点 (可选)'}),
        }