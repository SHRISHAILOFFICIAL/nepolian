from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/question/', views.password_reset_question, name='password_reset_question'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]
