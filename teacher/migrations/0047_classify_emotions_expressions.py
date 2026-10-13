from django.db import migrations


def classify_emotions(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Emotions').first()
    if not category:
        return
    assignments = [
["忍無可忍","Anger & Frustration"],
        ["我酸了","Sadness & Grief"],
        ["大驚小怪","Surprise & Mixed Feelings"],
        ["差強人意","Surprise & Mixed Feelings"],
        ["忐忑不安","Fear & Anxiety"],
        ["憤世嫉俗","Anger & Frustration"],
        ["興高采烈","Joy & Excitement"],
        ["心花怒放","Joy & Excitement"],
        ["喜出望外","Surprise & Mixed Feelings"],
        ["悲喜交加","Surprise & Mixed Feelings"],
        ["悵然若失","Sadness & Grief"]]
    def normalize(value):
        return ''.join(value.split()).replace('，', '').replace(',', '').replace('、', '').replace('。', '')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0046_classify_society_resource_expressions')]
    operations = [migrations.RunPython(classify_emotions, migrations.RunPython.noop)]
