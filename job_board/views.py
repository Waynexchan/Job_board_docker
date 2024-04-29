from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import csrf_protect
from .models import JobPosting, Company, Applicant, Application
from .forms import ApplicantSignUpForm, CompanySignUpForm,ApplicationForm,ApplicantInfoForm, CompanyUpdateForm, LoginForm, JobPostingForm, ApplicationStatusForm, CompanyInfoForm
import logging
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.exceptions import ValidationError



def index(request):
    active_postings = JobPosting.objects.filter(is_active=True)
    user_is_applicant = False
    user_is_company = False

    if request.user.is_authenticated:
        user_is_applicant = request.user.is_applicant
        user_is_company = request.user.is_company

    context = {
        "job_postings": active_postings,
        "user_is_applicant": user_is_applicant,
        "user_is_company": user_is_company  
    }

    return render(request, 'job_board/index.html', context)


def job_detail(request, pk):
    posting = get_object_or_404(JobPosting, pk=pk, is_active=True)
    user_is_applicant = False

    if request.user.is_authenticated and hasattr(request.user, 'applicant'):
        user_is_applicant = True
        applicant = request.user.applicant

        
        if not applicant.resume or not applicant.cover_letter:
            
            return redirect('update_applicant_info')

        
        existing_application = Application.objects.filter(
            applicant=applicant,
            job_posting=posting
        ).exists()

        if existing_application:
            messages.error(request, 'You have already applied for this job.')
            form = None  
        else:
            form = ApplicationForm()  

        if request.method == 'POST':
            form = ApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                application = form.save(commit=False)
                application.job_posting = posting
                application.applicant = applicant
                application.save()
                messages.success(request, 'Your application has been submitted.')
                return redirect('applicant_dashboard')
            else:
                messages.error(request, 'There was an error with your application.')
    else:
        form = None

    context = {
        "posting": posting,
        "form": form,
        "user_is_applicant": user_is_applicant
    }
    return render(request, 'job_board/detail.html', context)

User = get_user_model()

def send_activation_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('job_board/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    to_email = user.email
    send_mail(
        mail_subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  
        [to_email],
        fail_silently=False,
    )
    

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  
        if user.is_applicant:
            return redirect('update_applicant_info')
        elif user.is_company:
            return redirect('update_company_info')
        else:
            return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')



def register_applicant(request):
    if request.method == 'POST':
        form = ApplicantSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            send_activation_email(user, request)  
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            return render(request, 'job_board/register_applicant.html', {'form': form, 'error': 'Please revise the information provided.'})
    else:
        form = ApplicantSignUpForm()
    return render(request, 'job_board/register_applicant.html', {'form': form})

logger = logging.getLogger(__name__)

@login_required
def update_applicant_info(request):
    try:
        applicant = request.user.applicant
    except Applicant.DoesNotExist:
        applicant = Applicant(user=request.user)
        applicant.save()

    if request.method == 'POST':
        form = ApplicantInfoForm(request.POST, request.FILES, instance=applicant)
        if form.is_valid():
            form.save()
            logger.info('Applicant information updated successfully.')
            return redirect('applicant_dashboard')
        else:
            logger.error('Form is not valid. Errors: %s', form.errors)
    else:
        form = ApplicantInfoForm(instance=applicant)
    return render(request, 'job_board/update_applicant_info.html', {'form': form})

def register_company(request):
    if request.method == 'POST':
        form = CompanySignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            send_activation_email(user, request)  
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            return render(request, 'job_board/register_company.html', {'form': form, 'error': 'Please revise the information provided.'})
    else:
        form = CompanySignUpForm()
    return render(request, 'job_board/register_company.html', {'form': form})

@login_required
def update_company_info(request):
    try:
        company = request.user.company
    except Company.DoesNotExist:
        company = Company(user=request.user)
        company.save()

    if request.method == 'POST':
        form = CompanyInfoForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_dashboard')
    else:
        form = CompanyInfoForm(instance=company)
    return render(request, 'job_board/update_company_info.html', {'form': form})

logger = logging.getLogger(__name__)

@csrf_protect
def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if hasattr(user, 'is_applicant') and user.is_applicant:
                    return redirect('applicant_dashboard')
                else:
                    return redirect('company_dashboard')
            else:
                # Adding logging for failed login attempt
                logger.warning('Failed login attempt for username: %s', username)
                return render(request, 'job_board/login.html', {'form': form, 'error': 'Your username or password didn\'t match. Please try again.'})
        else:
            logger.warning('Login form is not valid. Errors: %s', form.errors)
    else:
        form = LoginForm()

    return render(request, 'job_board/login.html', {'form': form})
    
def user_logout(request):
    logout(request)
    return redirect('home')
    
def company_dashboard(request):
    if not request.user.is_company:
        return redirect('home')

    company = get_object_or_404(Company, user=request.user)
    job_postings = JobPosting.objects.filter(company=company)
    applications = Application.objects.filter(job_posting__company=company).select_related('applicant', 'job_posting')

    context = {
        'company': company,
        'job_postings': job_postings,
        'applications': applications
    }
    return render(request, 'job_board/company_dashboard.html', context)

def create_job_posting(request):
    company = get_object_or_404(Company, user=request.user)
    if not company.name or not company.address or not company.description:
        return redirect('update_company_info')
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.company = get_object_or_404(Company, user=request.user)
            job_posting.save()
            return redirect('company_dashboard')
    else:
        form = JobPostingForm()
    return render(request, 'job_board/create_job_posting.html', {'form': form})

def edit_job_posting(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk, company__user=request.user)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            form.save()
            return redirect('company_dashboard')
    else:
        form = JobPostingForm(instance=job_posting)
    
    return render(request, 'job_board/edit_job_posting.html', {'form': form})

def update_application_status(request, application_id):
    application = get_object_or_404(Application, pk=application_id, job_posting__company__user=request.user)
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect('company_dashboard')
    else:
        form = ApplicationStatusForm(instance=application)
    return render(request, 'job_board/update_application_status.html', {'form': form})

@login_required
def delete_job_posting(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk, company__user=request.user)
    
    if request.method == 'POST':
        applications = Application.objects.filter(job_posting=job_posting)
        for application in applications:
            application.status = 'DELETED'  
            application.save()

        job_posting.delete()
        messages.success(request, "The job posting has been deleted successfully.")
        return redirect('company_dashboard')
    else:
        context = {'job_posting': job_posting}
        return render(request, 'job_board/confirm_delete_job_posting.html', context)
    
def applicant_dashboard(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'applicant'):
        return redirect('home')

    applicant = request.user.applicant
    
    if not applicant.name or not applicant.address or not applicant.tel or not applicant.resume:
        return redirect('update_applicant_info')  

    job_postings = JobPosting.objects.filter(is_active=True)

    applications = Application.objects.filter(applicant=applicant).select_related('job_posting')

    context = {
        'job_postings': job_postings,
        'applications': applications  
    }
    return render(request, 'job_board/applicant_dashboard.html', context)

def applicant_info_view(request):
    if request.method == 'POST':
        form = ApplicantInfoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('applicant_dashboard') 
    else:
        form = ApplicantInfoForm()
    return render(request, 'applicant_info_form.html', {'form': form})

def apply_for_job(request, job_posting_id):
    job_posting = get_object_or_404(JobPosting, pk=job_posting_id, is_active=True)

    if not request.user.is_authenticated or not hasattr(request.user, 'applicant'):
        messages.error(request, "You need to be logged in and registered as an applicant.")
        return redirect('login')

    applicant = request.user.applicant

    if Application.objects.filter(applicant=applicant, job_posting=job_posting).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect('applicant_dashboard')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = applicant
            application.job_posting = job_posting
            
            # Check if applicant has already uploaded resume and cover letter
            existing_application = Application.objects.filter(applicant=applicant).first()
            if existing_application:
                # Use existing resume and cover letter if available
                application.resume = existing_application.resume
                application.cover_letter = existing_application.cover_letter
            
            application.save()
            messages.success(request, "Your application has been submitted successfully.")
            return redirect('applicant_dashboard')
    else:
        form = ApplicationForm()

    return render(request, 'job_board/apply_for_job.html', {'form': form, 'job_posting': job_posting})
