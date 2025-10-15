from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logs/', views.log_list, name='log_list'),
    path('logs/create/', views.create_log, name='create_log'),
    path('logs/<int:pk>/', views.log_detail, name='log_detail'),
    path('logs/<int:pk>/acknowledge/', views.acknowledge_log, name='acknowledge_log'),
]

