from django.db import migrations


def classify_daily_life_expressions(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    IdiomCategory = apps.get_model('teacher', 'IdiomCategory')

    daily_life = IdiomCategory.objects.filter(category_name__iexact='Daily Life').first()
    philosophy = IdiomCategory.objects.filter(category_name__iexact='Life & Philosophy').first()
    if not daily_life:
        return

    assignments = {
        '得寸進尺': 'Common Situations',
        '說者無意，聽者有心': 'Communication & Conversation',
        '一日之計在於晨': 'Habits & Routines',
        '今日事今日畢': 'Habits & Routines',
    }
    for expression, subcategory in assignments.items():
        Idiom.objects.filter(
            category_id=daily_life.pk, idiom=expression, subcategory=''
        ).update(subcategory=subcategory)

    if philosophy:
        Idiom.objects.filter(
            category_id=daily_life.pk, idiom='知足常樂'
        ).update(category_id=philosophy.pk, subcategory='Happiness & Contentment')


class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0033_idiom_subcategory'),
    ]

    operations = [
        migrations.RunPython(classify_daily_life_expressions, migrations.RunPython.noop),
    ]
