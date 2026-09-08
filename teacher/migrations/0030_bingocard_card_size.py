from django.db import migrations, models


def copy_existing_card_sizes(apps, schema_editor):
    BingoCard = apps.get_model('teacher', 'BingoCard')
    for card in BingoCard.objects.select_related('game').all().iterator():
        size = getattr(card.game, 'card_size', 3)
        if size not in (3, 4, 5):
            cell_count = len(card.cells or [])
            size = 3 if cell_count == 9 else 4 if cell_count == 16 else 5
        card.card_size = size
        card.save(update_fields=['card_size'])


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0029_bingo_multiple_rounds'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingocard',
            name='card_size',
            field=models.PositiveSmallIntegerField(
                choices=[(3, '3 x 3'), (4, '4 x 4'), (5, '5 x 5')],
                default=3,
            ),
        ),
        migrations.RunPython(copy_existing_card_sizes, migrations.RunPython.noop),
    ]
