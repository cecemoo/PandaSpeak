from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("student", "0026_timed_test_attempt"),
    ]

    operations = [
        migrations.RenameIndex(model_name="aiconversationusage", old_name="student_ai__student_88f06e_idx", new_name="student_aic_student_d29e88_idx"),
        migrations.RenameIndex(model_name="aiconversationusage", old_name="student_ai__kind_35fbbc_idx", new_name="student_aic_kind_ec342e_idx"),
    ]
