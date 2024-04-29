from django.urls import path
from django.contrib.auth.views import LoginView
from .views import (
    index, job_detail, register_applicant, register_company, custom_login, company_dashboard,
    create_job_posting, update_application_status, applicant_dashboard, apply_for_job, update_company_info, user_logout, update_applicant_info, edit_job_posting,delete_job_posting, activate
)

urlpatterns = [
    path('', index, name='home'),
    path('job/<int:pk>/', job_detail, name='job-detail'),
    path('register/applicant/', register_applicant, name='register_applicant'),
    path('register/company/', register_company, name='register_company'),
    path('accounts/login/', custom_login, name='login'),  
    path('company/dashboard/', company_dashboard, name='company_dashboard'),
    path('company/create_job_posting/', create_job_posting, name='create_job_posting'),
    path('company/update_application_status/<int:application_id>/', update_application_status, name='update_application_status'),
    path('applicant/dashboard/', applicant_dashboard, name='applicant_dashboard'),
    path('apply_for_job/<int:job_posting_id>/', apply_for_job, name='apply_for_job'),
    path('company/update_info/', update_company_info, name='update_company_info'),
    path('logout/', user_logout, name='logout'),
    path('applicant/update_info/', update_applicant_info, name='update_applicant_info'),
    path('job/edit/<int:pk>/', edit_job_posting, name='edit_job_posting'),
    path('activate/<uidb64>/<token>/',activate, name='activate'),
    path('job/delete/<int:pk>/', delete_job_posting, name='delete_job_posting'),


]
