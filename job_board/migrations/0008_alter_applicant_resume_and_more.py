# Generated by Django 5.0.4 on 2024-04-29 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0007_alter_application_job_posting_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to='resumes/'),
        ),
        migrations.AlterField(
            model_name='application',
            name='cover_letter',
            field=models.FileField(blank=True, null=True, upload_to='cover_letters/'),
        ),
    ]
