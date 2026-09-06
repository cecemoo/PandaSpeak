from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0005_studentgroup'),
        ('teacher', '0024_idiom_allowed_groups_idiom_visibility'),
    ]

    operations = [
        migrations.CreateModel(
            name='BingoGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content_type', models.CharField(choices=[('vocabulary', 'Vocabulary'), ('sentence', 'Sentences'), ('expression', 'Chinese Expressions')], default='vocabulary', max_length=20)),
                ('level', models.CharField(choices=[('level1', 'Level I'), ('level2', 'Level II'), ('level3', 'Level III'), ('all', 'All Levels')], default='level1', max_length=20)),
                ('card_size', models.PositiveSmallIntegerField(choices=[(3, '3 x 3'), (4, '4 x 4'), (5, '5 x 5')], default=5)),
                ('use_free_center', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bingo_games', to='course.studentgroup')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_bingo_games', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='BingoCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cells', models.JSONField(default=list)),
                ('marked_positions', models.JSONField(default=list)),
                ('has_bingo', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='teacher.bingogame')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bingo_cards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='bingocard',
            constraint=models.UniqueConstraint(fields=('game', 'student'), name='unique_bingo_card_per_student'),
        ),
    ]
