from django.db import migrations


# Restore only confirmed legacy expression classifications. Never overwrite edits.
VERIFIED = {
    '亡羊補牢': ('animals', 'Wisdom & Strategy'),
}


def backfill(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Sub = apps.get_model('teacher', 'LearningSubcategory')
    for idiom in Idiom.objects.filter(subcategory='', idiom__in=VERIFIED).select_related('category'):
        category_key, name = VERIFIED[idiom.idiom]
        if idiom.category and idiom.category.category_name.strip().lower() == category_key:
            if Sub.objects.filter(material_type='expression', category_id_value=idiom.category_id, name=name).exists():
                Idiom.objects.filter(pk=idiom.pk, subcategory='').update(subcategory=name)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0059_backfill_verified_vocabulary_subcategories')]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
