from django.db import migrations


def classify_numbers(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Numbers').first()
    if not category:
        return
    assignments = [
        ("一心一意", "Unity & Consistency"),
        ("三心二意", "Unity & Consistency"),
        ("一舉兩得", "Actions & Decisions"),
        ("一言不發", "Actions & Decisions"),
        ("二話不說", "Actions & Decisions"),
        ("四面八方", "Numbers & Quantities"),
        ("五花八門", "Numbers & Quantities"),
        ("六六大順", "Numbers & Quantities"),
        ("八九不離十", "Numbers & Quantities"),
        ("七上八下", "Emotions & Feelings"),
        ("十全十美", "Perfection & Repetition"),
        ("三番兩次", "Perfection & Repetition"),
    ]
    def normalize(value):
        return ''.join(value.split()).replace('，', '').replace(',', '').replace('、', '').replace('。', '')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0042_classify_colors_expressions')]
    operations = [migrations.RunPython(classify_numbers, migrations.RunPython.noop)]
