# main/forms.py
from django import forms
from .models import DailyReport, Task

class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReport
        # ここで task ではなく task_fk を使う！
        fields = ["date", "company", "product", "task_fk", "start_time", "end_time", "memo"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }
        labels = {
            "task_fk": "作業内容（選択）",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task_fk"].queryset = Task.objects.all().order_by("name")
        self.fields["task_fk"].empty_label = "（選択してください）"

    # 互換用：選んだら旧text側にも名前を入れておく（既存画面で使えるように）
    def save(self, commit=True):
        obj = super().save(commit=False)
        if obj.task_fk:
            obj.task = obj.task_fk.name
        if commit:
            obj.save()
        return obj
