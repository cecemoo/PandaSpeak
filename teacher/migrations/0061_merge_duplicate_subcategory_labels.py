from django.db import migrations


# The subcategory registry accumulated duplicate labels for the same
# subcategory: an English-only starter label (seeded by migration 0056,
# e.g. 'Head & Face') next to the canonical bilingual label used on the
# student pages (e.g. 'Head & Face 頭部與臉部'). Migration 0057 removed
# the starter labels only for categories whose name matched its list
# exactly and only when no items used them, so renamed categories such
# as 'Body Parts & Health' kept both forms. The Add Vocabulary dropdown
# and the manager page therefore offered two names for one subcategory,
# and words saved under the short form did not match the registry's
# canonical name.
#
# Merge rule (data-driven, no hardcoded category lists): within one
# material type + category, if a registry name is a strict prefix of
# exactly one other registry name followed by a space, the short name is
# the duplicate form. Move every item still carrying the short name to
# the long (canonical) name, then delete the short registry record.
# Names with zero or multiple long candidates are left untouched.


def merge_duplicate_labels(apps, schema_editor):
    Subcategory = apps.get_model('teacher', 'LearningSubcategory')
    item_models = {
        'vocabulary': apps.get_model('teacher', 'Vocabulary'),
        'sentence': apps.get_model('teacher', 'Sentence'),
        'expression': apps.get_model('teacher', 'Idiom'),
    }
    for kind, item_model in item_models.items():
        rows = list(Subcategory.objects.filter(material_type=kind))
        by_category = {}
        for row in rows:
            by_category.setdefault(row.category_id_value, []).append(row)
        for category_id, group in by_category.items():
            names = [row.name for row in group]
            for row in group:
                long_candidates = [
                    name for name in names
                    if name != row.name and name.startswith(row.name + ' ')
                ]
                if len(long_candidates) != 1:
                    continue
                canonical = long_candidates[0]
                item_model.objects.filter(
                    category_id=category_id, subcategory=row.name,
                ).update(subcategory=canonical)
                row.delete()


class Migration(migrations.Migration):
    dependencies = [('teacher', '0060_backfill_verified_expression_subcategories')]
    operations = [migrations.RunPython(merge_duplicate_labels, migrations.RunPython.noop)]
