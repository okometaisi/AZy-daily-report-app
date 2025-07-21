from django.db import models
from datetime import date 

class DailyReport(models.Model):
    date = models.DateField(default=date.today)  # 仮でOK！
    company = models.CharField(max_length=100, default='未設定')
    product = models.CharField(max_length=100, default='未設定')
    task = models.TextField(default='未設定')
    start_time = models.TimeField(default='05:30')
    end_time = models.TimeField(default='05:31')
    memo = models.TextField(blank=True)
    作業時間 = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.company} - {self.product}"
