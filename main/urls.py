from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('debts/', views.debt_list, name='debt_list'),
    path('debts/add/', views.debt_add, name='debt_add'),
    path('debts/<int:pk>/', views.debt_detail, name='debt_detail'),
    path('debts/<int:pk>/edit/', views.debt_edit, name='debt_edit'),
    path('debts/<int:pk>/delete/', views.debt_delete, name='debt_delete'),
    path('debts/<int:pk>/mark-paid/', views.debt_mark_paid, name='debt_mark_paid'),
    path('debts/<int:pk>/add-payment/', views.debt_add_payment, name='debt_add_payment'),
    path('debts/<int:pk>/pay-all/', views.debt_pay_all_customer, name='debt_pay_all_customer'),
    path('cashiers/', views.cashier_list, name='cashier_list'),
    path('cashiers/add/', views.cashier_add, name='cashier_add'),
    path('cashiers/<int:pk>/', views.cashier_detail, name='cashier_detail'),
    path('cashiers/<int:pk>/change-password/', views.cashier_change_password, name='cashier_change_password'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/import/', views.customer_import, name='customer_import'),
    path('api/customers/search/', views.customer_search_api, name='customer_search_api'),
    path('reminders/', views.reminders, name='reminders'),
    path('todays-operations/', views.todays_operations, name='todays_operations'),
    # Admin URLs (using 'manage' prefix to avoid conflict with Django's /admin/)
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/debts/', views.admin_all_debts, name='admin_all_debts'),
    path('manage/cashiers/', views.admin_cashier_list, name='admin_cashier_list'),
    path('manage/cashiers/add/', views.admin_cashier_add, name='admin_cashier_add'),
    path('manage/cashiers/<int:pk>/', views.admin_cashier_detail, name='admin_cashier_detail'),
    path('manage/cashiers/<int:pk>/change-password/', views.admin_cashier_change_password, name='admin_cashier_change_password'),
]

