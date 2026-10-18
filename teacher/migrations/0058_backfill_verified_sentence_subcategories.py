from django.db import migrations


# Only restore assignments whose text and category have been explicitly verified.
# Never overwrite a manager's saved choice or guess assignments for other rows.
VERIFIED = {
    '我很感謝我的家人。': 'Introducing Family Members 介紹家庭成員',
    '我的家人今天都在家。': 'Family Activities & Daily Life 家庭活動與日常生活',
}


def backfill(apps, schema_editor):
    Sentence = apps.get_model('teacher', 'Sentence')
    Subcategory = apps.get_model('teacher', 'LearningSubcategory')
    for sentence in Sentence.objects.filter(subcategory='').select_related('category'):
        if sentence.category.category_name.strip().lower() != 'family':
            continue
        name = VERIFIED.get(sentence.text.strip())
        if not name:
            continue
        if Subcategory.objects.filter(material_type='sentence',
                                      category_id_value=sentence.category_id,
                                      name=name).exists():
            Sentence.objects.filter(pk=sentence.pk, subcategory='').update(subcategory=name)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0057_sync_original_learning_subcategories')]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
