from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("course", "0016_group_course_enrollment"),
    ]

    operations = [
        migrations.RenameIndex(model_name="booking", old_name="course_book_session_5bd7e8_idx", new_name="course_book_session_fc9128_idx"),
        migrations.RenameIndex(model_name="groupclassrequest", old_name="course_grou_teacher_8d118f_idx", new_name="course_grou_teacher_e7099b_idx"),
        migrations.RenameIndex(model_name="groupclassrequest", old_name="course_grou_student_9b95df_idx", new_name="course_grou_student_19689b_idx"),
        migrations.RenameIndex(model_name="sessionattendance", old_name="course_sess_booking_4dad75_idx", new_name="course_sess_booking_65bf0f_idx"),
    ]
