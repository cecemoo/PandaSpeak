from django.db import migrations


def classify_nature(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Nature').first()
    if not category:
        return
    assignments = [["山明水秀","Nature & Landscapes"],["鏡花水月","Nature & Landscapes"],["遠在天邊，近在眼前","Nature & Landscapes"],["春暖花開","Weather & Seasons"],["夏天的陣雨，來得快去得快","Weather & Seasons"],["雪中送炭","Weather & Seasons"],["風雨同舟","Weather & Seasons"],["看花容易繡花難","Plants & Flowers"],["前人種樹，後人乘涼","Plants & Flowers"],["檀香木當柴燒，大材小用","Plants & Flowers"],["鮮花插在牛糞上","Plants & Flowers"],["水性楊花","Plants & Flowers"],["山窮水盡","Fire, Water & Natural Forces"],["紙包不住火","Fire, Water & Natural Forces"],["雪人烤火，不要命了","Fire, Water & Natural Forces"],["火冒三丈","Fire, Water & Natural Forces"],["水到渠成","Fire, Water & Natural Forces"],["除非太陽打西邊出來","Nature as Metaphor"],["天長地久","Nature as Metaphor"],["無風不起浪","Nature as Metaphor"],["不見高山，不顯平地","Nature as Metaphor"],["天無絕人之路","Nature as Metaphor"],["天機不可洩漏","Nature as Metaphor"],["常在河邊走，哪有不濕鞋","Nature as Metaphor"],["興風作浪","Nature as Metaphor"]]
    def normalize(value):
        return ''.join(c for c in value if c not in ' ，,、。！？!?：:；;\\t\\n')
    lookup = {normalize(expression): group for expression, group in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0050_classify_problems_expressions')]
    operations = [migrations.RunPython(classify_nature, migrations.RunPython.noop)]
