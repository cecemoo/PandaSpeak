from django.db import migrations

def classify_work_career(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Work & Career').first()
    if not category:
        return
    assignments = [["盆滿缽滿","Career Success & Achievement"],["杯水車薪","Workplace Challenges & Setbacks"],["埋頭苦幹","Hard Work & Dedication"]]
    def normalize(value):
        return ''.join(value.split()).replace('，', '').replace(',', '').replace('、', '').replace('。', '')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)

class Migration(migrations.Migration):
    dependencies = [('teacher', '0047_classify_emotions_expressions')]
    operations = [migrations.RunPython(classify_work_career, migrations.RunPython.noop)]
