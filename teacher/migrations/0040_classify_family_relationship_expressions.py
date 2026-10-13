from django.db import migrations


def classify_family_expressions(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Family & Relationships').first()
    if not category:
        return
    assignments = [
        ("家和萬事興", "Family Harmony & Values"),
        ("血濃於水", "Family Harmony & Values"),
        ("尊老愛幼", "Family Harmony & Values"),
        ("家醜不外揚", "Family Harmony & Values"),
        ("成家立業", "Family Harmony & Values"),
        ("形影不離", "Marriage & Couples"),
        ("天作之合", "Marriage & Couples"),
        ("夫妻本是同林鳥，大難來時各自飛", "Marriage & Couples"),
        ("夫唱婦隨", "Marriage & Couples"),
        ("舉案齊眉", "Marriage & Couples"),
        ("相見恨晚", "Love & Relationships"),
        ("情人眼裡出西施", "Love & Relationships"),
        ("相夫教子", "Parenting & Children"),
        ("一廂情願", "Love & Relationships"),
        ("任人擺佈", "Family Conflict & Difficulties"),
        ("投其所好", "Family Duties & Support"),
        ("各取所需", "Family Duties & Support"),
        ("求同存異", "Family Duties & Support"),
        ("有借有還，再借不難", "Family Duties & Support"),
        ("家家有本難唸的經", "Family Conflict & Difficulties"),
        ("癩蛤蟆想吃天鵝肉", "Love & Relationships"),
        ("社死", "Social Customs & Roles"),
        ("門當戶對", "Marriage & Couples"),
        ("白頭偕老", "Marriage & Couples"),
        ("重男輕女", "Social Customs & Roles"),
        ("一家之主", "Social Customs & Roles"),
        ("禮尚往來", "Social Customs & Roles"),
        ("淨身出戶", "Social Customs & Roles"),
    ]
    def normalize(value):
        return ''.join(value.split()).replace('，', ',').replace('、', ',').replace('。', '')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0039_classify_time_dates_expressions')]
    operations = [migrations.RunPython(classify_family_expressions, migrations.RunPython.noop)]
