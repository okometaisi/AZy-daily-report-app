from django.db import models
from datetime import date

# 会社名モデル（使わないなら置いておいてOK）
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

# 商品名モデル（使わないなら置いておいてOK）
class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    class Meta:
        unique_together = ("company", "name")
    def __str__(self):
        return f"{self.company} / {self.name}"

# 作業内容マスタ（新規の選択肢用）
class Task(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

# 作業テンプレート（商品ごとに工程セットを保存）
class TaskPreset(models.Model):
    label = models.CharField(max_length=100)              # 例: JSW100標準
    content = models.TextField()                          # 例: 手入れ　清掃　塗装　検査　梱包
    product = models.CharField(max_length=100, blank=True, null=True)  # 対象商品名（空なら共通）
    sort_order = models.PositiveIntegerField(default=1000)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "label"]

    def __str__(self):
        return f"{self.product or '共通'} / {self.label}"

class DailyReport(models.Model):
    date = models.DateField(default=date.today)

    # 既存どおり：文字列のまま
    company = models.CharField(max_length=100, default='未設定')
    product = models.CharField(max_length=100, default='未設定')
    task    = models.TextField(default='未設定')

    # 新規：選択式で使う外部キー（ここだけ追加）
    task_fk = models.ForeignKey(Task, on_delete=models.PROTECT, null=True, blank=True, verbose_name="作業内容（選択）")

    start_time = models.TimeField(default='05:30')
    end_time   = models.TimeField(default='05:31')
    memo = models.TextField(blank=True)
    作業時間 = models.DurationField(null=True, blank=True)

    def __str__(self):
        show_task = self.task_fk.name if self.task_fk else self.task
        return f"{self.date} - {self.company} - {show_task}"


