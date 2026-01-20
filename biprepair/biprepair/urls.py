"""
URL configuration for biprepair project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
from django.views.generic import TemplateView
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path

from appointments import views as appointment_views

urlpatterns = [
    path('admin/', appointment_views.admin_login, name='admin_root'),
    path('service-worker.js', appointment_views.service_worker, name='service_worker'),
    path('', include('appointments.urls')),
]
