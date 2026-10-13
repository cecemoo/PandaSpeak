from django.db import migrations


def classify_friendship(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Friendship').first()
    if not category:
        return
    assignments = [
        ("無話不談", "Friendship & Affection"),
        ("志同道合", "Making Friends"),
        ("一見如故", "Making Friends"),
        ("患難見真情", "Trust & Loyalty"),
        ("兩肋插刀", "Support & Encouragement"),
        ("肝膽相照", "Trust & Loyalty"),
        ("情同手足", "Friendship & Affection"),
        ("臭味相投", "Making Friends"),
        ("酒肉朋友", "Friendship & Betrayal"),
        ("路遙知馬力，日久見人心", "Trust & Loyalty"),
        ("君子一言，駟馬難追", "Trust & Loyalty"),
        ("忘恩負義", "Friendship & Betrayal"),
        ("同流合污", "Social Relationships"),
        ("知無不言，言無不盡", "Trust & Loyalty"),
        ("患難之交", "Friendship & Affection"),
    ]
    for expression, subcategory in assignments:
        Idiom.objects.filter(
            category_id=category.pk, idiom=expression, subcategory=''
        ).update(subcategory=subcategory)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0037_classify_advanced_philosophy')]
    operations = [
        migrations.RunPython(classify_friendship, migrations.RunPython.noop),
    ]
