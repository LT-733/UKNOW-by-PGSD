"""
URL configuration for frontend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include
from frontendapp import views
from oauth2_provider import urls as oauth2_urls
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('result/', views.result, name='result'),
    path('detail/', views.detail, name='detail'),
    path('api/', include('api.urls')),
    path('o/', include(oauth2_urls)),
    path('auth/callback/', views.oauth_callback, name='oauth_callback'),
    path('register/', views.register, name='register'),
    
    # Built-in Login/Logout (no view code needed!)
    path('login/', auth_views.LoginView.as_view(template_name='frontendapp/templates/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # The form where they type the new password
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='frontendapp/templates/password_change.html',
        success_url='/password_change/done/'
    ), name='password_change'),

    # The "Success" message page
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='frontendapp/templates/password_change_done.html'
    ), name='password_change_done'),
]
