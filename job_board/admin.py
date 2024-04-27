from django.contrib import admin
from .models import JobPosting, Application, Applicant, Company
from .forms import ApplicationAdminForm, CompanyAdminForm

admin.site.register(JobPosting)
admin.site.register(Application)

class ApplicantAdmin(admin.ModelAdmin):
    add_form = ApplicationAdminForm
    list_display = ['name', 'user', 'address', 'tel']
    fields = ['name', 'address', 'tel', 'resume', 'cover_letter']
    
    def save_model(self, request, obj, form, change):
        if not change:
            user_form = self.add_form(request.POST)
            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.is_applicant = True
                user.save()
                obj.user = user
        super().save_model(request, obj, form, change)

admin.site.register(Applicant, ApplicantAdmin)

class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm
    list_display = ['name', 'user', 'address', 'co_type']
    fields = ['user', 'name', 'address', 'description', 'co_type']
    
    def save_model(self, request, obj, form, change):
        if not change:
            user_form = self.add_form(request.POST)
            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.is_company = True
                user.save()
                obj.user = user
        super().save_model(request, obj, form, change)

admin.site.register(Company, CompanyAdmin)