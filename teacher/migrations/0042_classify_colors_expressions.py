from django.db import migrations


def classify_colors(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Colors').first()
    if not category:
        return
    assignments = [
        ("五顏六色", "Colors & Appearance"),
        ("五彩繽紛", "Colors & Appearance"),
        ("一片漆黑", "Colors & Appearance"),
        ("黑白分明", "Clarity & Truth"),
        ("顛倒黑白", "Clarity & Truth"),
        ("白紙黑字", "Clarity & Truth"),
        ("面紅耳赤", "Emotions & Facial Expressions"),
        ("臉色蒼白", "Emotions & Facial Expressions"),
        ("臉都綠了", "Emotions & Facial Expressions"),
        ("青出於藍", "Success & Recognition"),
        ("燈紅酒綠", "Descriptions & Metaphors"),
        ("萬紫千紅", "Colors & Appearance"),
        ("近朱者赤近墨者黑", "Descriptions & Metaphors"),
    ]
    def normalize(value):
        return ''.join(value.split()).replace('，', '').replace(',', '').replace('、', '').replace('。', '')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0041_classify_body_parts_expressions')]
    operations = [migrations.RunPython(classify_colors, migrations.RunPython.noop)]
