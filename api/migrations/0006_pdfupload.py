# Generated by Django 5.1 on 2024-09-30 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_rename_generatedpdf_sortedpdf_plan_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='PdfUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weights_file', models.FileField(upload_to='uploads/')),
                ('batches_file', models.FileField(upload_to='uploads/')),
                ('can1', models.TextField()),
                ('hydro', models.TextField()),
                ('line3', models.TextField()),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
