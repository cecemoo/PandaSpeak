from django.db import migrations


def classify_time_dates(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Time & Dates').first()
    if not category:
        return
    assignments = [
        ("時間就是金錢", "Time Is Precious"),
        ("一寸光陰一寸金", "Time Is Precious"),
        ("光陰似箭", "Time Is Precious"),
        ("爭分奪秒", "Time Is Precious"),
        ("分秒必爭", "Time Is Precious"),
        ("一時半刻", "Punctuality & Timing"),
        ("無時無刻", "Punctuality & Timing"),
        ("早起的鳥兒有蟲吃", "Time Management & Productivity"),
        ("一年之計在於春", "Time Management & Productivity"),
        ("明日復明日，明日何其多", "Time Management & Productivity"),
        ("日積月累", "Time Management & Productivity"),
        ("日月如梭", "Passing Time & Change"),
        ("歲月不饒人", "Passing Time & Change"),
        ("曾幾何時", "Passing Time & Change"),
        ("物換星移", "Passing Time & Change"),
        ("一日三秋", "Passing Time & Change"),
        ("度日如年", "Passing Time & Change"),
        ("等到猴年馬月", "Patience & Waiting"),
        ("來日方長", "Patience & Waiting"),
        ("十年樹木，百年樹人", "Patience & Waiting"),
        ("冰凍三尺，非一日之寒", "Patience & Waiting"),
        ("羅馬不是一天造成的", "Patience & Waiting"),
        ("機不可失，時不再來", "Opportunities & Deadlines"),
        ("把握當下", "Opportunities & Deadlines"),
        ("夜長夢多", "Opportunities & Deadlines"),
        ("稍縱即逝", "Opportunities & Deadlines"),
        ("有朝一日", "Opportunities & Deadlines"),
        ("時不我予", "Opportunities & Deadlines"),
    ]
    # Match common spacing and punctuation differences without editing the stored text.
    def normalize(value):
        return ''.join(value.split()).replace('，', ',').replace('、', ',').replace('。', '').replace('兒', '兒')

    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        subcategory = lookup.get(normalize(item.idiom))
        if subcategory:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=subcategory)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0038_classify_friendship_expressions')]
    operations = [
        migrations.RunPython(classify_time_dates, migrations.RunPython.noop),
    ]
