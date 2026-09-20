from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('student', '0023_cultural_insights'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CulturalInsightCompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_slug', models.SlugField(max_length=100)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cultural_insight_completions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-completed_at']},
        ),
        migrations.AddConstraint(
            model_name='culturalinsightcompletion',
            constraint=models.UniqueConstraint(fields=('student', 'lesson_slug'), name='unique_student_cultural_lesson_completion'),
        ),
    ]
