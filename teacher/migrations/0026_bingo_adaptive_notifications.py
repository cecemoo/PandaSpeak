from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0025_bingogame_bingocard'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingogame',
            name='adaptive_difficulty',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='bingocard',
            name='assigned_level',
            field=models.CharField(default='level1', max_length=20),
        ),
        migrations.AddField(
            model_name='bingocard',
            name='moves_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='bingocard',
            name='teacher_notified',
            field=models.BooleanField(default=False),
        ),
    ]
