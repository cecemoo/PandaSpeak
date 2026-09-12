from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0030_bingocard_card_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingogame',
            name='category_key',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='bingogame',
            name='content_type',
            field=models.CharField(
                choices=[
                    ('vocabulary', 'Vocabulary'),
                    ('sentence', 'Sentences'),
                    ('expression', 'Chinese Expressions'),
                ],
                default='vocabulary',
                max_length=20,
            ),
        ),
    ]
