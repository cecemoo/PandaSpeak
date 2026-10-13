from django.db import migrations

def classify_people(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='People').first()
    if not category:
        return
    assignments = [["天賦異稟","Personality & Character"],["心不在焉","Personality & Character"],["陰陽怪氣","Personality & Character"],["還是那張嘴","Personality & Character"],["人心不足蛇吞象","Personality & Character"],["自我膨脹","Personality & Character"],["自以為是","Personality & Character"],["優柔寡斷","Personality & Character"],["飄飄欲仙","Personality & Character"],["急病亂投醫","Speech & Behavior"],["放鴿子","Speech & Behavior"],["說曹操曹操到","Speech & Behavior"],["東一榔頭西一棒子","Speech & Behavior"],["刀子嘴豆腐心","Speech & Behavior"],["只聽樓梯響不見人下來","Speech & Behavior"],["老王賣瓜自賣自誇","Speech & Behavior"],["吊兒郎當","Speech & Behavior"],["一視同仁","Speech & Behavior"],["看破不說破","Judgment & Perception"],["前無古人後無來者","Judgment & Perception"],["取人之長補己之短","Judgment & Perception"],["求人不如求己","Judgment & Perception"],["人不犯我我不犯人","Judgment & Perception"],["成也蕭何敗也蕭何","Judgment & Perception"],["難伺候","Difficulties & Survival"],["有兩把刷子","Difficulties & Survival"],["吃得苦中苦方為人上人","Difficulties & Survival"],["大難不死必有後福","Difficulties & Survival"],["泥菩薩過河自身難保","Difficulties & Survival"],["槍桿頂上看人把人看矮了","Difficulties & Survival"],["啞巴吃餃子心裡有數","Humor & Everyday Sayings"],["像和尚借梳子找錯了對象","Humor & Everyday Sayings"],["小巷子裡扛竹竿轉不過彎來","Humor & Everyday Sayings"]]
    def normalize(value):
        return ''.join(c for c in value if c not in ' ，,、。！？!?：:；;\t\n')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)

class Migration(migrations.Migration):
    dependencies = [('teacher', '0048_classify_work_career_expressions')]
    operations = [migrations.RunPython(classify_people, migrations.RunPython.noop)]
