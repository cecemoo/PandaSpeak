from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0028_bingo_game_modes_and_accuracy'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='bingocard',
            name='unique_bingo_card_per_student',
        ),
        migrations.AddField(
            model_name='bingocard',
            name='round_number',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddConstraint(
            model_name='bingocard',
            constraint=models.UniqueConstraint(fields=('game', 'student', 'round_number'), name='unique_bingo_round_per_student'),
        ),
        migrations.AlterModelOptions(
            name='bingocard',
            options={'ordering': ['-created_at']},
        ),
    ]
