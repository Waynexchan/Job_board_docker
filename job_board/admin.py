from django.contrib import admin

# Register your models here.

from .models import JobPosting, Applicant, Company, Application

admin.site.register(JobPosting)
admin.site.register(Applicant)
admin.site.register(Company)
admin.site.register(Application)
