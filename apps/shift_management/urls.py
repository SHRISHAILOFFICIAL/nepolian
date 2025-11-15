from django.urls import path
from . import views

urlpatterns = [
    path('', views.shift_list_view, name='shift_list'),
    path('my-shifts/', views.my_shifts_view, name='my_shifts'),
    path('<int:shift_id>/', views.shift_detail_view, name='shift_detail'),
    path('<int:shift_id>/volunteer/', views.volunteer_for_shift, name='volunteer_for_shift'),
    path('application/<int:application_id>/withdraw/', views.withdraw_volunteer, name='withdraw_volunteer'),
    
    # Manager URLs
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/create/', views.create_shift, name='create_shift'),
    path('manager/<int:shift_id>/update/', views.update_shift, name='update_shift'),
    path('manager/<int:shift_id>/cancel/', views.cancel_shift, name='cancel_shift'),
    path('manager/application/<int:application_id>/review/', views.review_volunteer, name='review_volunteer'),
    path('manager/application/<int:application_id>/approve/', views.approve_volunteer, name='approve_volunteer'),
    path('manager/application/<int:application_id>/reject/', views.reject_volunteer, name='reject_volunteer'),
]
