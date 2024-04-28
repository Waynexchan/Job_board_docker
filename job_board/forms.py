from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Applicant, Company, Application, JobPosting

class ApplicantSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Enter a valid email address")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_applicant = True
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            Applicant.objects.create(user=user)
        return user
    
class ApplicantInfoForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True, label="Full Name")
    address = forms.CharField(max_length=255, required=True, label="Address")
    tel = forms.CharField(max_length=20, required=True, label="Telephone")
    resume = forms.FileField(required=True, label="Resume", help_text="Upload your resume.")
    cover_letter = forms.FileField(required=False, label="Cover Letter", help_text="Optional: Upload your cover letter in PDF format.")

    class Meta:
        model = Applicant
        fields = ['name', 'address', 'tel', 'resume', 'cover_letter']

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume and not resume.name.endswith('.pdf'):
            raise ValidationError("Only PDF files are accepted for resumes.")
        return resume

    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if cover_letter and not cover_letter.name.endswith('.pdf'):
            raise ValidationError("Only PDF files are accepted for cover letters.")
        return cover_letter
    
class ApplicationAdminForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_applicant = True  
        if commit:
            user.save()
        return user

class CompanySignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company = True
        if commit:
            user.save()
        return user
    
class CompanyInfoForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Company
        fields = ['name', 'address', 'description']
    
class CompanyAdminForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company = True  
        if commit:
            user.save()
        return user
    
class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'salary', 'is_active']

class ApplicationForm(forms.ModelForm):
    cover_letter = forms.FileField(
        required=False,
        help_text="Optional: Upload your cover letter in PDF format."
    )
    portfolio = forms.FileField(
        required=False,
        help_text="Optional: Upload your portfolio or additional documents."
    )
    
    class Meta:
        model = Application
        fields = ['cover_letter', 'portfolio']

    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if cover_letter and not cover_letter.name.endswith('.pdf'):
            raise ValidationError("Only PDF files are accepted for cover letters.")
        return cover_letter

    def clean_portfolio(self):
        portfolio = self.cleaned_data.get('portfolio')
        if portfolio and not portfolio.name.endswith('.pdf'):
            raise ValidationError("Only PDF files are accepted for portfolios.")
        return portfolio

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            })
        }

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class CompanyUpdateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'description']

