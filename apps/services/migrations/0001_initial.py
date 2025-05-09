# Generated by Django 5.1.7 on 2025-04-20 23:40

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_delete_clientprofile'),
        ('category', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_category', to='category.category')),
                ('expert', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='accounts.expertuserprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('agreed_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('end_date', models.DateField(help_text='Expected completion date provided by the client.')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('in_progress', 'In Progress'), ('awaiting_confirmation', 'Awaiting Confirmation'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=50)),
                ('expert_response_reason', models.TextField(blank=True, null=True)),
                ('expert_completed', models.BooleanField(default=False)),
                ('expert_completion_date', models.DateTimeField(blank=True, null=True)),
                ('client_confirmed', models.BooleanField(default=False)),
                ('confirmation_date', models.DateTimeField(blank=True, null=True)),
                ('has_dispute', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to=settings.AUTH_USER_MODEL)),
                ('expert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engagements', to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='services.service')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['status'], name='services_se_status_9254ae_idx'), models.Index(fields=['client'], name='services_se_client__a89f06_idx'), models.Index(fields=['expert'], name='services_se_expert__fe1393_idx'), models.Index(fields=['status', 'client'], name='services_se_status_0eba57_idx'), models.Index(fields=['status', 'expert'], name='services_se_status_93f4df_idx'), models.Index(fields=['created_at'], name='services_se_created_fe46d7_idx')],
            },
        ),
    ]
