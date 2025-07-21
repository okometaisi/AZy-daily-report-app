from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('report/input/', views.report_input, name='report_input'),
    path('report/list/', views.report_list, name='report_list'),
    path('report/edit/<int:report_id>/', views.report_edit, name='report_edit'),
    path('report/delete/<int:report_id>/', views.report_delete, name='report_delete'),
    path('report/summary/', views.report_summary, name='report_summary'),
    path('report/comparison/', views.report_comparison, name='report_comparison'),
    


]
