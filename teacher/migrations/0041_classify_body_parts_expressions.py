from django.db import migrations


def classify_body_parts(apps, schema_editor):
    Idiom = apps.get_model('teacher', 'Idiom')
    Category = apps.get_model('teacher', 'IdiomCategory')
    category = Category.objects.filter(category_name__iexact='Body Parts').first()
    if not category:
        return
    assignments = [
        ("目瞪口呆", "Eyes & Observation"),
        ("眼見為憑", "Eyes & Observation"),
        ("目光短淺", "Eyes & Observation"),
        ("一目十行過目不忘", "Eyes & Observation"),
        ("眼高手低", "Eyes & Observation"),
        ("耳目一新", "Eyes & Observation"),
        ("眉開眼笑", "Heart & Emotions"),
        ("耳聽為虛，眼見為實", "Ears & Listening"),
        ("耳濡目染", "Ears & Listening"),
        ("七嘴八舌", "Mouth & Speech"),
        ("心直口快", "Mouth & Speech"),
        ("病從口入，禍從口出。", "Mouth & Speech"),
        ("油嘴滑舌", "Mouth & Speech"),
        ("口是心非", "Mouth & Speech"),
        ("肺腑之言", "Mouth & Speech"),
        ("血口噴人", "Mouth & Speech"),
        ("伶牙俐齒", "Mouth & Speech"),
        ("心服口服", "Heart & Emotions"),
        ("心照不宣", "Heart & Emotions"),
        ("心心相印", "Heart & Emotions"),
        ("心思不宣", "Heart & Emotions"),
        ("一心不能二用", "Mindset & Character"),
        ("手忙腳亂", "Hands, Feet & Actions"),
        ("躡手躡腳", "Hands, Feet & Actions"),
        ("手足情深", "Human Relationships"),
        ("手到擒來", "Hands, Feet & Actions"),
        ("手足無措", "Hands, Feet & Actions"),
        ("遊手好閒", "Hands, Feet & Actions"),
        ("踢手踢腳", "Hands, Feet & Actions"),
        ("身弱屈膝", "Physical Appearance & Health"),
        ("麻雀雖小，五臟俱全", "Physical Appearance & Health"),
        ("瘦骨如柴", "Physical Appearance & Health"),
        ("粉身碎骨", "Physical Appearance & Health"),
        ("胸有成竹", "Mindset & Character"),
        ("得人心者得天下 失人心者失天下", "Human Relationships"),
        ("頭頭是道", "Mouth & Speech"),
        ("拋頭露面", "Mindset & Character"),
        ("手心手背都是肉", "Human Relationships"),
        ("百聞不如一見", "Eyes & Observation"),
        ("骨肉相連", "Human Relationships"),
    ]
    def normalize(value):
        return ''.join(value.split()).replace('，', ',').replace('、', ',').replace('。', '').replace('！', '!')
    lookup = {normalize(expression): subcategory for expression, subcategory in assignments}
    for item in Idiom.objects.filter(category_id=category.pk, subcategory='').only('pk', 'idiom'):
        target = lookup.get(normalize(item.idiom))
        if target:
            Idiom.objects.filter(pk=item.pk, subcategory='').update(subcategory=target)


class Migration(migrations.Migration):
    dependencies = [('teacher', '0040_classify_family_relationship_expressions')]
    operations = [migrations.RunPython(classify_body_parts, migrations.RunPython.noop)]
