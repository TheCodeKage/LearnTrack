from django.urls import path
from django.contrib.auth import views as auth_views

from users import views
from users.forms import LoginForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('get-progress/', views.get_progress, name='get_progress'),
]