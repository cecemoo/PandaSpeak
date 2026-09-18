from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0013_course_group_tutoring'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupClassRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200)),
                ('level', models.CharField(choices=[('level1','Level I'),('level2','Level II'),('level3','Level III')], default='level1', max_length=10)),
                ('preferred_times', models.CharField(max_length=500)),
                ('desired_group_size', models.PositiveIntegerField(default=4)),
                ('message', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending','Pending'),('accepted','Accepted'),('declined','Declined'),('converted','Class Created')], default='pending', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='originating_group_requests', to='course.course')),
                ('source_course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_class_requests', to='course.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_class_requests', to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_class_requests_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(model_name='groupclassrequest', index=models.Index(fields=['teacher','status'], name='course_grou_teacher_8d118f_idx')),
        migrations.AddIndex(model_name='groupclassrequest', index=models.Index(fields=['student','status'], name='course_grou_student_9b95df_idx')),
    ]
