from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [('student', '0025_historylessoncompletion')]
    operations = [
        migrations.AddField(model_name='languagetest', name='time_limit_minutes', field=models.PositiveIntegerField(blank=True, null=True, help_text='Optional time limit per student in minutes')),
        migrations.CreateModel(name='TimedTestAttempt', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('started_at', models.DateTimeField(auto_now_add=True)),
            ('deadline', models.DateTimeField()),
            ('draft_answers', models.JSONField(blank=True, default=dict)),
            ('completed_at', models.DateTimeField(blank=True, null=True)),
            ('auto_submitted', models.BooleanField(default=False)),
            ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.languagetest')),
        ]),
        migrations.AddConstraint(model_name='timedtestattempt', constraint=models.UniqueConstraint(fields=('student','test'), name='unique_timed_test_attempt')),
    ]
