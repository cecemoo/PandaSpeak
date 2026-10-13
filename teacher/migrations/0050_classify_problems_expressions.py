from django.db import migrations

def classify_problems(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Problems & Challenges & Situations').first()
    if not category:
        return
    assignments = [["燙手山芋","Difficulties & Setbacks"],["徒勞無功","Difficulties & Setbacks"],["一錘子買賣","Difficulties & Setbacks"],["勢如破竹","Difficulties & Setbacks"],["寥寥無幾","Difficulties & Setbacks"],["屋漏偏逢連夜雨","Difficulties & Setbacks"],["禍不單行","Difficulties & Setbacks"],["履見不鮮","Difficulties & Setbacks"],["不容小覷","Difficulties & Setbacks"],["破釜沉舟","Difficulties & Setbacks"],["種瓜得瓜","Causes & Consequences"],["自作自受","Causes & Consequences"],["欲蓋彌彰","Causes & Consequences"],["暗渡陳倉","Causes & Consequences"],["惹是生非","Causes & Consequences"],["隨機應變","Solutions & Coping"],["走投無路","Solutions & Coping"],["大事化小小事化無","Solutions & Coping"],["小題大做","Solutions & Coping"],["忍一時風平浪靜退一步海闊天空","Solutions & Coping"],["帶節奏","Solutions & Coping"],["巧婦難為無米之炊","Solutions & Coping"],["兩害相權取其輕","Conflict & Dilemmas"],["多此一舉","Conflict & Dilemmas"],["當局者迷旁觀者清","Conflict & Dilemmas"],["出岔子","Conflict & Dilemmas"],["天方夜譚","Unexpected Situations"],["潛移默化","Unexpected Situations"],["甕中捉鱉","Unexpected Situations"],["撲朔迷離","Unexpected Situations"]]
    def normalize(value):
        return ''.join(c for c in value if c not in ' ，,、。！？!?：:；;\t\n')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)

class Migration(migrations.Migration):
    dependencies = [('teacher', '0049_classify_people_expressions')]
    operations = [migrations.RunPython(classify_problems, migrations.RunPython.noop)]
