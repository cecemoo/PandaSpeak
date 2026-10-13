from django.db import migrations


def classify_society_resource(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Society & Resource').first()
    if not category:
        return
    assignments = [
        ("人盡其才，物盡其用，地盡其利，貨暢其流", "Resources & Value"),
        ("物以稀為貴", "Resources & Value"),
        ("物超所值", "Resources & Value"),
        ("一榮俱榮一損俱損", "Cooperation & Interdependence"),
        ("唇亡齒寒", "Cooperation & Interdependence"),
        ("勞心者治人，勞力者治於人", "Public Welfare & Responsibility"),
        ("集思廣益", "Cooperation & Interdependence"),
        ("打擦邊球", "Social Behavior & Opportunity"),
        ("無心插柳柳成蔭", "Social Behavior & Opportunity"),
        ("人山人海", "Social Behavior & Opportunity"),
        ("法不輕傳，道不賤賣", "Resources & Value"),
        ("曇花一現", "Social Behavior & Opportunity"),
        ("至高無上", "Wealth & Social Status"),
        ("有錢能使鬼推磨", "Wealth & Social Status"),
        ("名不虛傳", "Wealth & Social Status"),
        ("手慢無", "Social Behavior & Opportunity"),
    ]
    def normalize(value):
        return ''.join(value.split()).replace('，', '').replace(',', '').replace('、', '').replace('。', '')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0045_classify_weather_expressions')]
    operations = [migrations.RunPython(classify_society_resource, migrations.RunPython.noop)]
