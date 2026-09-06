from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0026_bingo_adaptive_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingogame',
            name='audience',
            field=models.CharField(
                choices=[
                    ('group', 'One Student Group'),
                    ('my_students', 'All My Students'),
                    ('subscribers', 'All PandaSpeak Subscribers'),
                ],
                default='group',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='bingogame',
            name='student_group',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bingo_games',
                to='course.studentgroup',
            ),
        ),
    ]
