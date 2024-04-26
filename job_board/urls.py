from django.urls import path
from django.contrib.auth.views import LoginView
from .views import register_applicant,register_company
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('job/<int:pk>/', views.job_detail, name='job-detail'),
    path('register/applicant/', register_applicant, name='register_applicant'),
    path('register/company/', register_company, name='register_company'),
    path('login/', LoginView.as_view(template_name='job_board/login.html'), name='login'),
]
