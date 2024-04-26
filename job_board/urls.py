from django.urls import path
from django.contrib.auth.views import LoginView
from .views import (
    index, job_detail, register_applicant, register_company, custom_login, company_dashboard,
    create_job_posting, update_application_status, applicant_dashboard, apply_for_job
)

urlpatterns = [
    path('', index, name='home'),
    path('job/<int:pk>/', job_detail, name='job-detail'),
    path('register/applicant/', register_applicant, name='register_applicant'),
    path('register/company/', register_company, name='register_company'),
    path('login/', custom_login, name='login'),  
    path('company/dashboard/', company_dashboard, name='company_dashboard'),
    path('company/create_job_posting/', create_job_posting, name='create_job_posting'),
    path('company/update_application_status/<int:application_id>/', update_application_status, name='update_application_status'),
    path('applicant/dashboard/', applicant_dashboard, name='applicant_dashboard'),
    path('apply_for_job/<int:job_posting_id>/', apply_for_job, name='apply_for_job'),
]
