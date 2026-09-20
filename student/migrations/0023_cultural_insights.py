from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('student', '0022_ai_conversation_usage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CulturalInsight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('chinese_title', models.CharField(blank=True, max_length=200)),
                ('level', models.CharField(choices=[('level2', 'Level II'), ('level3', 'Level III')], max_length=10)),
                ('category', models.CharField(choices=[('daily', 'Daily Life & Etiquette'), ('festival', 'Festivals & Traditions'), ('food', 'Food & Dining'), ('language', 'Language & Communication'), ('society', 'Society & Relationships'), ('history', 'History & Heritage'), ('regional', 'Regional Culture'), ('modern', 'Modern Culture')], default='daily', max_length=20)),
                ('summary', models.CharField(max_length=350)),
                ('content', models.TextField()),
                ('useful_chinese', models.TextField(blank=True, help_text='Optional useful Traditional Chinese words or expressions.')),
                ('did_you_know', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='cultural_insights/')),
                ('audio', models.FileField(blank=True, null=True, upload_to='cultural_insights/audio/')),
                ('is_published', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['level', 'order', 'title']},
        ),
        migrations.CreateModel(
            name='CulturalInsightUnlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unlocked_at', models.DateTimeField(auto_now_add=True)),
                ('insight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_unlocks', to='student.culturalinsight')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cultural_insight_unlocks', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-unlocked_at']},
        ),
        migrations.AddConstraint(
            model_name='culturalinsightunlock',
            constraint=models.UniqueConstraint(fields=('student', 'insight'), name='unique_student_cultural_insight'),
        ),
    ]
