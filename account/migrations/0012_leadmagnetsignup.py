# Generated for the free BoPoMoFo chart lead magnet (2026-10-07).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_customuser_news_emails_announcement_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadMagnetSignup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('source', models.CharField(default='bopomofo-chart', max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('unsubscribed', models.BooleanField(default=False)),
                ('followup_day2_sent', models.BooleanField(default=False)),
                ('followup_day5_sent', models.BooleanField(default=False)),
            ],
        ),
    ]
