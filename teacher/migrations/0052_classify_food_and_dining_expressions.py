from django.db import migrations


def classify_food_and_dining(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Food and Dining').first()
    if not category:
        return
    assignments = [["小菜一碟","Food & Ingredients"],["雞蛋裡挑骨頭","Food & Ingredients"],["生米已成熟飯","Food & Ingredients"],["狼吞虎嚥","Cooking & Preparation"],["細嚼慢嚥","Cooking & Preparation"],["挑肥揀瘦","Cooking & Preparation"],["食指大動","Eating & Appetite"],["飢不擇食","Eating & Appetite"],["畫餅充飢","Eating & Appetite"],["秀色可餐","Taste & Flavor"],["民以食為天","Dining Etiquette & Sharing"],["喝水不忘掘井人","Dining Etiquette & Sharing"]]
    def normalize(value):
        return ''.join(c for c in value if c not in ' ，,、。！？!?：:；;\\t\\n')
    lookup = {normalize(expression): group for expression, group in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0051_classify_nature_expressions')]
    operations = [migrations.RunPython(classify_food_and_dining, migrations.RunPython.noop)]
