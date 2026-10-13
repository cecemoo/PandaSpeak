from django.db import migrations


def classify_life_philosophy(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    IdiomCategory = apps.get_model('teacher', 'IdiomCategory')
    category = IdiomCategory.objects.filter(category_name__iexact='Life & Philosophy').first()
    if not category:
        return

    assignments = {
        '活到老，學到老': 'Wisdom & Life Lessons',
        '過了這個村就沒這個店兒': 'Wisdom & Life Lessons',
        '獨一無二': 'Values & Principles',
        '舉一反三': 'Personal Growth',
        '長痛不如短痛': 'Attitude & Mindset',
        '順其自然': 'Attitude & Mindset',
        '一分耕耘，一分收穫': 'Success & Failure',
        '知足常樂': 'Happiness & Contentment',
    }
    for expression, subcategory in assignments.items():
        Idiom.objects.filter(
            category_id=category.pk, idiom=expression,
            subcategory__in=['', subcategory],
        ).update(subcategory=subcategory)


class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0034_classify_daily_life_expressions'),
    ]

    operations = [
        migrations.RunPython(classify_life_philosophy, migrations.RunPython.noop),
    ]
