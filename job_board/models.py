
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from config import settings

class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='job_postings')
    salary = models.IntegerField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} | {self.company} | Active: {self.is_active}"
    
class Applicant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    tel = models.CharField(max_length=20)
    cover_letter = models.FileField(upload_to='cover_letters/', default='No cover letter provided')
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected')
    ]

    def __str__(self):
        return f'{self.name} | {self.user.email}'

    def save(self, *args, **kwargs):
        if not self.user.is_applicant:
            raise ValueError("Assigned user is not marked as an applicant")
        super().save(*args, **kwargs)
    
class Company(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    INDUSTRY_CHOICES =[
        ('IT', 'Information Technology'),
        ('FIN', 'Finance'),
        ('EDU', 'Education'),
        ('HEA', 'Healthcare'),
        ('MAN', 'Manufacturing'),
        ('AGR', 'Agriculture'),
        ('RET', 'Retail'),
        ('WH', 'Warehousing'),
        ('TRN', 'Transportation'),
        ('CON', 'Construction'),
        ('ENT', 'Entertainment'),
        ('FOOD', 'Food & Beverages'),
        ('HOS', 'Hospitality'),
        ('REA', 'Real Estate'),
        ('GOV', 'Government'),
        ('NGO', 'Non-profit Organization'),
        ('LAW', 'Law'),
        ('SRV', 'Service Industry'),
        ('ADV', 'Advertising'),
        ('AUT', 'Automotive'),
        ('TEL', 'Telecommunications'),
        ('ENE', 'Energy'),
        ('PHR', 'Pharmaceutical'),
        ('BIOT', 'Biotechnology'),
        ('FASH', 'Fashion'),
        ('MED', 'Media'),
        ('PUB', 'Publishing'),
        ('COS', 'Cosmetics'),
        ('ART', 'Art & Design'),
        ('RESE', 'Research & Development'),
        ('Others', 'Others')
    ]
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    description = models.TextField()
    co_type = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, default='IT')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.user.is_company:
            raise ValueError("Assigned user is not marked as a company")
        super().save(*args, **kwargs)
    
class Application(models.Model):
    job_posting = models.ForeignKey(JobPosting, on_delete=models.SET_NULL, null=True, related_name='applications')
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.FileField(upload_to='cover_letters/', null=True, blank=True)
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('DELETED', 'Job Posting Deleted')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    application_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('applicant', 'job_posting')

    def __str__(self):
        return f'{self.applicant.name} applied for {self.job_posting.title} | Status: {self.status}'

class CustomUser(AbstractUser): 
    is_applicant = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)