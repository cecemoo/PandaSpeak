from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0016_personalflashcard'),
        ('teacher', '0032_alter_bingogame_category_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalflashcard',
            name='source_idiom',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='personal_flashcards',
                to='teacher.idiom',
            ),
        ),
        migrations.AddField(
            model_name='personalflashcard',
            name='source_sentence',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='personal_flashcards',
                to='teacher.sentence',
            ),
        ),
        migrations.AddField(
            model_name='personalflashcard',
            name='source_vocabulary',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='personal_flashcards',
                to='teacher.vocabulary',
            ),
        ),
    ]
