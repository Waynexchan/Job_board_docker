from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from .models import JobPosting, Company, Applicant, Application
from .forms import ApplicantSignUpForm, CompanySignUpForm,ApplicationForm, CompanyUpdateForm,LoginForm, JobPostingForm, ApplicationStatusForm, CompanyInfoForm


def index(request):
    active_postings = JobPosting.objects.filter(is_active=True)
    context = {
        "job_postings": active_postings
    }
    return render(request, 'job_board/index.html', context)

def job_detail(request, pk):
    posting = get_object_or_404(JobPosting, pk=pk, is_active=True)
    context = {
        "posting": posting
    }
    return render(request, 'job_board/detail.html', context)

def register_applicant(request):
    if request.method == 'POST':
        form = ApplicantSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'job_board/register_applicant.html', {'form': form, 'error': 'Please revise the information provided.'})
    else:
        form = ApplicantSignUpForm()
    return render(request, 'job_board/register_applicant.html', {'form': form})

def register_company(request):
    if request.method == 'POST':
        form = CompanySignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('update_company_info')  
        else:
            return render(request, 'job_board/register_company.html', {'form': form, 'error': 'Please revise the information provided.'})
    else:
        form = CompanySignUpForm()
    return render(request, 'job_board/register_company.html', {'form': form})

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
                return render(request, 'job_board/login.html', {'form': form, 'error': 'Your Username and password didn\'t match. Please try again.'})
        else:
            return render(request, 'job_board/login.html', {'form': form})
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
    if not company.name or not company.address or not company.description:
        return redirect('update_company_info')
    
    job_postings = JobPosting.objects.filter(company=company)
    context = {
        'company': company,
        'job_postings': job_postings
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

def applicant_dashboard(request):
    if not request.user.is_applicant:
        return redirect('home') 
    
    job_postings = JobPosting.objects.filter(is_active=True)
    context = {
        'job_postings': job_postings
    }
    return render(request, 'job_board/applicant_dashboard.html', context)

def apply_for_job(request, job_posting_id):
    job_posting = get_object_or_404(JobPosting, pk=job_posting_id, is_active=True)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = get_object_or_404(Applicant, user=request.user)
            application.job_posting = job_posting
            application.save()
            return redirect('applicant_dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'job_board/apply_for_job.html', {'form': form, 'job_posting': job_posting})