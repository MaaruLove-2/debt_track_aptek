from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('debts/', views.debt_list, name='debt_list'),
    path('debts/add/', views.debt_add, name='debt_add'),
    path('debts/<int:pk>/', views.debt_detail, name='debt_detail'),
    path('debts/<int:pk>/mark-paid/', views.debt_mark_paid, name='debt_mark_paid'),
    path('pharmacists/', views.pharmacist_list, name='pharmacist_list'),
    path('pharmacists/add/', views.pharmacist_add, name='pharmacist_add'),
    path('pharmacists/<int:pk>/', views.pharmacist_detail, name='pharmacist_detail'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/import/', views.customer_import, name='customer_import'),
    path('api/customers/search/', views.customer_search_api, name='customer_search_api'),
    path('reminders/', views.reminders, name='reminders'),
    # Admin URLs (using 'manage' prefix to avoid conflict with Django's /admin/)
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/debts/', views.admin_all_debts, name='admin_all_debts'),
    path('manage/pharmacists/', views.admin_pharmacist_list, name='admin_pharmacist_list'),
    path('manage/pharmacists/add/', views.admin_pharmacist_add, name='admin_pharmacist_add'),
    path('manage/pharmacists/<int:pk>/', views.admin_pharmacist_detail, name='admin_pharmacist_detail'),
    path('manage/pharmacists/<int:pk>/change-password/', views.admin_pharmacist_change_password, name='admin_pharmacist_change_password'),
]

