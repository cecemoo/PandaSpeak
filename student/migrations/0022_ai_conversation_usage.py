from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('student', '0021_personalflashcard')]
    operations = [
        migrations.CreateModel(
            name='AICachedSpeech',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cache_key', models.CharField(max_length=64, unique=True)),
                ('voice', models.CharField(max_length=20)),
                ('text', models.TextField()),
                ('audio', models.BinaryField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AIConversationUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('reply','AI Reply'),('speech','AI Speech')], max_length=10)),
                ('model_name', models.CharField(blank=True, max_length=100)),
                ('input_units', models.PositiveIntegerField(default=0)),
                ('output_units', models.PositiveIntegerField(default=0)),
                ('estimated_cost_usd', models.DecimalField(decimal_places=6, default=0, max_digits=10)),
                ('cached', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_conversation_usage', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering':['-created_at']},
        ),
        migrations.AddIndex(model_name='aiconversationusage', index=models.Index(fields=['student','created_at'], name='student_ai__student_88f06e_idx')),
        migrations.AddIndex(model_name='aiconversationusage', index=models.Index(fields=['kind','created_at'], name='student_ai__kind_35fbbc_idx')),
    ]
