from django.db import migrations


def classify_weather(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Weather').first()
    if not category:
        return
    assignments = [
        ("風和日麗", "Pleasant Weather & Scenery"),
        ("晴空萬里", "Pleasant Weather & Scenery"),
        ("萬里無雲", "Pleasant Weather & Scenery"),
        ("秋高氣爽", "Pleasant Weather & Scenery"),
        ("晴天霹靂", "Weather Metaphors & Life Lessons"),
        ("烈日當空", "Extreme Weather"),
        ("寒風刺骨", "Extreme Weather"),
        ("大雨滂沱", "Rain & Thunder"),
        ("傾盆大雨", "Rain & Thunder"),
        ("雷雨交加", "Rain & Thunder"),
        ("電閃雷鳴", "Rain & Thunder"),
        ("狂風暴雨", "Wind & Storms"),
        ("風雨無阻", "Weather Metaphors & Life Lessons"),
        ("雨過天晴", "Weather Metaphors & Life Lessons"),
        ("水土不服", "Weather Metaphors & Life Lessons"),
        ("風調雨順", "Wind & Storms"),
        ("未雨綢繆", "Weather Metaphors & Life Lessons"),
        ("雷聲大雨點小", "Weather Metaphors & Life Lessons"),
        ("風聲鶴唳", "Weather Metaphors & Life Lessons"),
        ("春風得意", "Weather Metaphors & Life Lessons"),
        ("天有不測風雲", "Weather Metaphors & Life Lessons"),
    ]
    def normalize(value):
        return ''.join(value.split()).replace('，', '').replace(',', '').replace('、', '').replace('。', '')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0044_classify_animals_expressions')]
    operations = [migrations.RunPython(classify_weather, migrations.RunPython.noop)]
