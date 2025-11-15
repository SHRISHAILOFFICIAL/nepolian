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
    
    # Admin user management URLs
    path('users/', views.user_management_view, name='user_management'),
    path('users/create/', views.create_user_view, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user_view, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user_view, name='delete_user'),
]
