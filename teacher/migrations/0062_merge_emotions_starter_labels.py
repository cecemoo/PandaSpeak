from django.db import migrations


# The Emotions vocabulary category still carries the three English-only
# starter labels seeded by migration 0056 — 'Positive Emotions',
# 'Negative Emotions', 'Feelings & Reactions' — next to the canonical
# bilingual labels synced by migration 0057 ('Happiness & Positive
# Feelings 快樂與正面情緒', 'Sadness & Negative Feelings 悲傷與負面情緒',
# 'Anger & Frustration 生氣與挫折', 'Fear & Worry 害怕與擔心',
# 'Surprise & Mixed Feelings 驚訝與複雜感受'). Migration 0061's prefix
# rule could not merge them: the starter labels are not prefixes of the
# canonical names. The Add Vocabulary dropdown therefore offers two
# names for the same groupings.
#
# Merge rule (vocabulary, Emotions category only — the sentence labels
# from the same seed are canonical, not duplicates):
# - 'Positive Emotions' -> 'Happiness & Positive Feelings 快樂與正面情緒'
# - 'Negative Emotions' -> 'Sadness & Negative Feelings 悲傷與負面情緒'
# - 'Feelings & Reactions' has no canonical equivalent (it duplicated
#   the category itself): its items return to Not assigned ('') and the
#   registry record is deleted.

MERGES = {
    'Positive Emotions': 'Happiness & Positive Feelings 快樂與正面情緒',
    'Negative Emotions': 'Sadness & Negative Feelings 悲傷與負面情緒',
}
REMOVE_UNASSIGNED = ['Feelings & Reactions']


def merge_emotions_labels(apps, schema_editor):
    Category = apps.get_model('teacher', 'VocabularyCategory')
    Vocabulary = apps.get_model('teacher', 'Vocabulary')
    Subcategory = apps.get_model('teacher', 'LearningSubcategory')

    category_ids = [
        category.pk
        for category in Category.objects.all()
        if category.category_name.strip().lower() == 'emotions'
    ]
    for category_id in category_ids:
        for old_name, canonical in MERGES.items():
            Subcategory.objects.get_or_create(
                material_type='vocabulary',
                category_id_value=category_id,
                name=canonical,
            )
            Vocabulary.objects.filter(
                category_id=category_id, subcategory=old_name,
            ).update(subcategory=canonical)
            Subcategory.objects.filter(
                material_type='vocabulary',
                category_id_value=category_id,
                name=old_name,
            ).delete()
        for old_name in REMOVE_UNASSIGNED:
            Vocabulary.objects.filter(
                category_id=category_id, subcategory=old_name,
            ).update(subcategory='')
            Subcategory.objects.filter(
                material_type='vocabulary',
                category_id_value=category_id,
                name=old_name,
            ).delete()


class Migration(migrations.Migration):
    dependencies = [('teacher', '0061_merge_duplicate_subcategory_labels')]
    operations = [migrations.RunPython(merge_emotions_labels, migrations.RunPython.noop)]
