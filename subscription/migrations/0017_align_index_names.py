from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("subscription", "0016_merge_school_and_blocklist"),
    ]

    operations = [
        migrations.RenameIndex(model_name="studentactivity", old_name="subscriptio_user_id_47b7c1_idx", new_name="subscriptio_user_id_89693e_idx"),
        migrations.RenameIndex(model_name="studentactivity", old_name="subscriptio_activit_14b42c_idx", new_name="subscriptio_activit_4ad508_idx"),
    ]
