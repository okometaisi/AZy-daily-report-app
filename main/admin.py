from django.contrib import admin
from .models import Company, Product, Task, DailyReport, TaskPreset

admin.site.register(Company)
admin.site.register(Product)
admin.site.register(Task)
admin.site.register(DailyReport)

@admin.register(TaskPreset)
class TaskPresetAdmin(admin.ModelAdmin):
    list_display  = ("label", "product", "is_active", "sort_order")
    list_filter   = ("is_active", "product")
    search_fields = ("label", "product", "content")
    ordering      = ("sort_order", "label")
