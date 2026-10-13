from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0032_alter_bingogame_category_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='idiom',
            name='subcategory',
            field=models.CharField(blank=True, db_index=True, default='', max_length=100),
        ),
    ]
