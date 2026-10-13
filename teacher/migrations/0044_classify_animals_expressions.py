from django.db import migrations


def classify_animals(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Animals').first()
    if not category:
        return
    assignments = [
        ("膽小如鼠", "Personality & Behavior"),
        ("九牛一毛", "Animal Characteristics & Comparisons"),
        ("騎虎難下", "Danger & Difficulties"),
        ("守株待兔", "Wisdom & Strategy"),
        ("望子成龍", "Success & Achievement"),
        ("畫蛇添足", "Wisdom & Strategy"),
        ("馬到成功", "Success & Achievement"),
        ("亡羊補牢", "Wisdom & Strategy"),
        ("殺雞儆猴", "Wisdom & Strategy"),
        ("雞同鴨講", "Relationships & Society"),
        ("狗急跳牆", "Danger & Difficulties"),
        ("扮豬吃老虎", "Wisdom & Strategy"),
        ("牛頭不對馬嘴", "Relationships & Society"),
        ("馬馬虎虎", "Personality & Behavior"),
        ("飛蛾撲火", "Danger & Difficulties"),
        ("呆若木雞", "Personality & Behavior"),
        ("天下烏鴉一般黑", "Relationships & Society"),
        ("初生之犢不怕虎", "Courage & Strength"),
        ("老鼠過街人人喊打", "Relationships & Society"),
        ("貓哭老鼠假慈悲", "Personality & Behavior"),
        ("往狗嘴裡拋骨頭，投其所好", "Wisdom & Strategy"),
        ("熱鍋上的螞蟻", "Danger & Difficulties"),
        ("黃鼠狼給雞拜年，沒安好心", "Danger & Difficulties"),
        ("貓捉老鼠狗看門，各盡其職", "Relationships & Society"),
        ("井底之蛙", "Wisdom & Strategy"),
        ("雞飛狗跳", "Personality & Behavior"),
        ("賊眉鼠眼", "Personality & Behavior"),
        ("指鹿為馬", "Wisdom & Strategy"),
        ("一石二鳥", "Success & Achievement"),
        ("鳥語花香", "Animal Characteristics & Comparisons"),
    ]
    def normalize(value):
        return ''.join(value.split()).replace('，', '').replace(',', '').replace('、', '').replace('。', '')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0043_classify_numbers_expressions')]
    operations = [migrations.RunPython(classify_animals, migrations.RunPython.noop)]
