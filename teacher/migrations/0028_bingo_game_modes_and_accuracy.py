from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0027_bingogame_audience_nullable_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingogame',
            name='game_mode',
            field=models.CharField(
                choices=[
                    ('listening', 'Listening Bingo'),
                    ('make_sentence', 'Make-Sentence Bingo'),
                ],
                default='listening',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='bingogame',
            name='content_type',
            field=models.CharField(
                choices=[
                    ('vocabulary', 'Vocabulary'),
                    ('sentence', 'Sentences'),
                ],
                default='vocabulary',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='bingocard',
            name='correct_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='bingocard',
            name='incorrect_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
