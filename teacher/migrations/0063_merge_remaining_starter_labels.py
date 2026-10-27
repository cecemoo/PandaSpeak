from django.db import migrations


# Full-vocabulary sweep of the remaining 0056 starter labels, following
# migration 0062 (Emotions). Migration 0057 added the canonical bilingual
# labels but deleted only the GENERIC starter set, and only when unused;
# migration 0061 merged starter labels that are strict prefixes of one
# canonical name. What remains are starter labels that duplicate a
# canonical grouping under a different wording (e.g. verbs 'Actions'
# next to 'Everyday Actions 日常動作'). This migration merges each one
# into its canonical equivalent — items keep their grouping under the
# canonical name — or, where the starter bucket spans several canonical
# groups and has no honest equivalent (e.g. food 'Food & Ingredients'),
# returns its items to Not assigned ('') and deletes the registry record.
#
# Scope: vocabulary only (the sentence labels from the same seed are the
# canonical sentence taxonomy, not duplicates), and only the categories
# listed below. Categories with no canonical bilingual list in 0057
# (nature, places, transportation) keep their starter labels — those are
# their only labels, not duplicates. Emotions is covered by 0062.

# category key (lowercased category name) -> {starter label: canonical
# label or None}. None means: unassign items, delete the registry record.
MAPPINGS = {
    'adjectives': {
        'Quality': 'Appearance & Qualities 外觀與特質',
    },
    'adverbs': {
        'Frequency': 'Time & Frequency 時間與頻率副詞',
    },
    'animals': {
        'Sea Animals': 'Aquatic Animals 水生動物',
    },
    'colors': {
        'Shades & Descriptions': 'Color Descriptions 顏色描述',
    },
    'daily life': {
        'Household Items': 'Home & Personal Items 居家與個人物品',
        'Personal Care': 'Home & Personal Items 居家與個人物品',
        'Routines': 'Morning & Evening Routines 早晚作息',
    },
    'food': {
        'Food & Ingredients': None,
        'Cooking': None,
        'Dining': 'Meals & Dishes 餐點與料理',
    },
    'food and dining': {
        'Food & Ingredients': None,
        'Cooking': None,
        'Dining': 'Meals & Dishes 餐點與料理',
    },
    'numbers': {
        'Quantities': 'Counting & Quantities 數量與計數',
    },
    'people': {
        'Family Members': 'People & Identity 人物與身分',
        'Personality & Character': 'Personality & Descriptions 個性與人物描述',
        'Relationships': 'Friends & Relationships 朋友與人際關係',
        'Descriptions of People': 'Personality & Descriptions 個性與人物描述',
    },
    'shopping': {
        'Shopping Items': None,
        'Sizes & Quantities': 'Clothing & Sizes 衣服與尺寸',
    },
    'time & dates': {
        'Time': 'Time of Day 一天中的時間',
        'Dates': 'Days & Weeks 日期與星期',
    },
    'verbs': {
        'Actions': 'Everyday Actions 日常動作',
        'Communication': 'Speaking & Communication 說話與溝通',
        'Daily Activities': 'Everyday Actions 日常動作',
    },
}


def merge_remaining_labels(apps, schema_editor):
    Category = apps.get_model('teacher', 'VocabularyCategory')
    Vocabulary = apps.get_model('teacher', 'Vocabulary')
    Subcategory = apps.get_model('teacher', 'LearningSubcategory')

    for category in Category.objects.all():
        mapping = MAPPINGS.get(category.category_name.strip().lower())
        if not mapping:
            continue
        for old_name, canonical in mapping.items():
            if canonical is not None:
                Subcategory.objects.get_or_create(
                    material_type='vocabulary',
                    category_id_value=category.pk,
                    name=canonical,
                )
                Vocabulary.objects.filter(
                    category_id=category.pk, subcategory=old_name,
                ).update(subcategory=canonical)
            else:
                Vocabulary.objects.filter(
                    category_id=category.pk, subcategory=old_name,
                ).update(subcategory='')
            Subcategory.objects.filter(
                material_type='vocabulary',
                category_id_value=category.pk,
                name=old_name,
            ).delete()


class Migration(migrations.Migration):
    dependencies = [('teacher', '0062_merge_emotions_starter_labels')]
    operations = [migrations.RunPython(merge_remaining_labels, migrations.RunPython.noop)]
