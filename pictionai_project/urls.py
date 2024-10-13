"""
URL configuration for pictionai_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from pictionai_app import views  # Update to use your app name

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Homepage
    path('submit_guess/', views.submit_guess, name='submit_guess'),  # Form submission
    path('result/', views.result, name='result'),  # Result page
]
