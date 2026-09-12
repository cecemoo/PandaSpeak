from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0031_bingogame_category_key_and_expression'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bingogame',
            name='category_key',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
