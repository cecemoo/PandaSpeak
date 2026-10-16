from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('teacher', '0054_sync_expression_topics')]
    operations = [
        migrations.AddField(model_name='vocabulary', name='subcategory', field=models.CharField(max_length=100, blank=True, default='')),
        migrations.AddField(model_name='sentence', name='subcategory', field=models.CharField(max_length=100, blank=True, default='')),
    ]
