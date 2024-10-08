# Generated by Django 5.1 on 2024-09-30 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_pdfupload'),
    ]

    operations = [
        migrations.CreateModel(
            name='FailedPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_id', models.CharField(max_length=10)),
                ('batches', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('progress', models.CharField(blank=True, default='in-progress', max_length=20, null=True)),
                ('order', models.IntegerField(default=-1)),
                ('line', models.CharField(blank=True, default='line', max_length=100, null=True)),
                ('error_details', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
