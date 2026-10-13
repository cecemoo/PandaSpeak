from django.db import migrations


def classify_advanced_daily_life(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    IdiomCategory = apps.get_model('teacher', 'IdiomCategory')
    category = IdiomCategory.objects.filter(category_name__iexact='Daily Life').first()
    if not category:
        return
    assignments = {
        "一言為定": "Decisions & Choices",
        "色香味俱全": "Everyday Activities",
        "津津有味": "Everyday Activities",
        "回味無窮": "Everyday Activities",
        "大快朵頤": "Everyday Activities",
        "山珍海味": "Everyday Activities",
        "潤了": "Common Situations",
        "不屑一顧": "Behavior & Personality",
        "深思熟慮": "Decisions & Choices",
        "口若懸河": "Communication & Conversation",
        "格格不入": "Common Situations",
        "斤斤計較": "Behavior & Personality",
        "悶悶不樂": "Emotions & Reactions",
        "爾虞我詐": "Behavior & Personality",
        "一概而論": "Communication & Conversation",
        "江郎才盡": "Difficulties & Challenges",
        "胡言亂語": "Communication & Conversation",
        "鬼話連篇": "Communication & Conversation",
        "口不擇言": "Communication & Conversation",
        "使出渾身解數": "Difficulties & Challenges",
        "忍氣吞聲": "Emotions & Reactions",
        "你行你上 不行別BB": "Communication & Conversation",
        "說不過去 / 站不住腳": "Common Situations",
        "沒轍了": "Difficulties & Challenges",
        "勉強過得去": "Common Situations",
        "不讓自負膨脹": "Behavior & Personality",
        "手頭緊": "Difficulties & Challenges",
        "教科書式的操作方法": "Everyday Activities",
        "自得其樂": "Emotions & Reactions",
        "井井有條": "Habits & Routines",
        "事半功倍": "Habits & Routines",
    }
    for expression, subcategory in assignments.items():
        Idiom.objects.filter(
            category_id=category.pk, idiom=expression, subcategory=''
        ).update(subcategory=subcategory)

    # Support punctuation variants without modifying the expression itself.
    Idiom.objects.filter(
        category_id=category.pk, idiom__startswith='說不過去',
        subcategory=''
    ).update(subcategory='Common Situations')
    Idiom.objects.filter(
        category_id=category.pk, idiom__startswith='你行你上',
        subcategory=''
    ).update(subcategory='Communication & Conversation')


class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0035_classify_life_philosophy_expressions'),
    ]
    operations = [
        migrations.RunPython(classify_advanced_daily_life, migrations.RunPython.noop),
    ]
