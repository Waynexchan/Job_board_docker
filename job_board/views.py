from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from .models import JobPosting
from .forms import ApplicantSignUpForm, CompanySignUpForm


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
            form.save()
            return redirect('login')
        else:
            return render(request, 'job_board/register_company.html', {'form': form, 'error': 'Please revise the information provided.'})
    else:
        form = CompanySignUpForm()
    return render(request, 'job_board/register_company.html', {'form': form})

@csrf_protect
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_applicant:
                return redirect('applicant_dashboard')
            else:
                return redirect('company_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Login Fail.'})
    else:
        return render(request, 'login.html')