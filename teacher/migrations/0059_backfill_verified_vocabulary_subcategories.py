from django.db import migrations


# Verified legacy vocabulary entry; avoid guessing other existing assignments.
VERIFIED_VOCABULARY = {
    '忠誠': 'Values & Morality 價值與道德',
}


def backfill(apps, schema_editor):
    Vocabulary = apps.get_model('teacher', 'Vocabulary')
    Subcategory = apps.get_model('teacher', 'LearningSubcategory')
    for item in Vocabulary.objects.filter(subcategory='', word__in=VERIFIED_VOCABULARY).select_related('category'):
        if item.category.category_name.strip().lower() != 'abstract ideas / concepts':
            continue
        name = VERIFIED_VOCABULARY[item.word]
        if Subcategory.objects.filter(material_type='vocabulary',
                                      category_id_value=item.category_id, name=name).exists():
            Vocabulary.objects.filter(pk=item.pk, subcategory='').update(subcategory=name)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0058_backfill_verified_sentence_subcategories')]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
