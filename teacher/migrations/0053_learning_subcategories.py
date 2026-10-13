from django.db import migrations, models

def seed(apps, schema_editor):
    Idiom=apps.get_model('teacher','Idiom')
    Sub=apps.get_model('teacher','LearningSubcategory')
    for cid,name in Idiom.objects.exclude(category_id=None).exclude(subcategory='').values_list('category_id','subcategory').distinct():
        Sub.objects.get_or_create(material_type='expression',category_id_value=cid,name=name)

class Migration(migrations.Migration):
    dependencies=[('teacher','0052_classify_food_and_dining_expressions')]
    operations=[migrations.CreateModel(name='LearningSubcategory',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('material_type',models.CharField(max_length=20,choices=[('vocabulary','Vocabulary'),('sentence','Sentences'),('expression','Chinese Expressions')])),('category_id_value',models.PositiveIntegerField()),('name',models.CharField(max_length=100))]),migrations.AddConstraint(model_name='learningsubcategory',constraint=models.UniqueConstraint(fields=('material_type','category_id_value','name'),name='unique_learning_subcategory')),migrations.RunPython(seed,migrations.RunPython.noop)]
