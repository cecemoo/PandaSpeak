from django.db import migrations


def classify_advanced_philosophy(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Life & Philosophy').first()
    if not category:
        return
    assignments = [
        ("一帆風順", "Success & Failure"),
        ("久仰大名", "Human Nature & Relationships"),
        ("命裡有時終須有，命裡無時莫強求", "Attitude & Mindset"),
        ("隨遇而安", "Attitude & Mindset"),
        ("人生如戲，戲如人生", "Wisdom & Life Lessons"),
        ("世事無常，活在當下", "Wisdom & Life Lessons"),
        ("人算不如天算", "Wisdom & Life Lessons"),
        ("佛系", "Attitude & Mindset"),
        ("四兩撥千斤", "Wisdom & Life Lessons"),
        ("一絲不苟", "Values & Principles"),
        ("學以致用", "Personal Growth"),
        ("煙消雲散", "Time & Opportunity"),
        ("死馬當活馬醫", "Attitude & Mindset"),
        ("無功不受祿", "Values & Principles"),
        ("畫餅", "Wisdom & Life Lessons"),
        ("秤砣雖小壓千斤", "Wisdom & Life Lessons"),
        ("過了這個村兒就沒這個店兒", "Time & Opportunity"),
        ("命運多舛", "Time & Opportunity"),
        ("足智多謀", "Personal Growth"),
        ("不入虎穴焉得虎子", "Success & Failure"),
        ("晚節不保", "Values & Principles"),
        ("水可載舟，亦可覆舟", "Wisdom & Life Lessons"),
        ("人不可貌相，海水不可斗量", "Wisdom & Life Lessons"),
        ("人情世故", "Human Nature & Relationships"),
        ("鬼斧神工", "Wisdom & Life Lessons"),
        ("人生如逆水行舟不進則退", "Personal Growth"),
        ("萬無一失", "Success & Failure"),
        ("全力以赴", "Success & Failure"),
        ("不惜一切代價", "Values & Principles"),
        ("本末倒置", "Wisdom & Life Lessons"),
        ("如釋重負", "Happiness & Contentment"),
        ("及時行樂", "Happiness & Contentment"),
        ("一棒子打死", "Attitude & Mindset"),
        ("操之過急", "Attitude & Mindset"),
        ("推己及人", "Values & Principles"),
        ("己所不欲勿施於人", "Values & Principles"),
        ("弱肉強食", "Human Nature & Relationships"),
        ("由儉入奢易由奢入儉難", "Wisdom & Life Lessons"),
        ("凡走過必留下痕跡", "Wisdom & Life Lessons"),
        ("融會貫通", "Personal Growth"),
        ("失敗為成功之母", "Success & Failure"),
        ("讀萬卷書，行萬里路", "Personal Growth"),
        ("行勝於言", "Values & Principles"),
        ("少壯不努力，老大徒傷悲", "Time & Opportunity"),
        ("溫故知新", "Personal Growth"),
        ("事過境遷", "Time & Opportunity"),
        ("天行健 君子以自強不息", "Personal Growth"),
        ("天下無難事，只怕有心人", "Success & Failure"),
        ("福無雙至，禍不單行", "Cause & Effect"),
        ("戲台上的鼓槌，一對", "Human Nature & Relationships"),
        ("偷來的鑼鼓打不得", "Values & Principles"),
        ("熟能生巧", "Personal Growth"),
        ("有志者事竟成", "Success & Failure"),
        ("物以類聚", "Human Nature & Relationships"),
        ("學到用時方恨少", "Personal Growth"),
    ]
    for expression, subcategory in assignments:
        Idiom.objects.filter(category_id=category.pk, idiom=expression, subcategory='').update(subcategory=subcategory)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0036_classify_advanced_daily_life')]
    operations = [
        migrations.RunPython(classify_advanced_philosophy, migrations.RunPython.noop),
    ]
