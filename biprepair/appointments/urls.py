from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('status/', views.check_status, name='check_status'),
    path('clients/login/', views.client_login, name='client_login'),
    path('clients/logout/', views.client_logout, name='client_logout'),
    path('clients/register/', views.client_register, name='client_register'),
    path('clients/contact/', views.contact_admin, name='contact_admin'),
    path('clients/contact/history/', views.contact_admin_history, name='contact_admin_history'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/register/', views.admin_register, name='admin_register'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/appointments/', views.admin_appointments, name='admin_appointments'),
    path('admin/appointments/<str:appointment_id>/', views.admin_detail, name='admin_detail'),
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('admin/messages/<int:message_id>/', views.admin_message_detail, name='admin_message_detail'),
    path('admin/clients/', views.admin_clients, name='admin_clients'),
    path('admin/clients/<int:client_id>/', views.admin_client_detail, name='admin_client_detail'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('tos/', views.terms_of_service, name='terms_of_service'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('tracking/', views.tracking_policy, name='tracking_policy'),
]
