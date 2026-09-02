from django.test import TestCase

from account.models import CustomUser

from .forms import StudentGroupForm
from .models import StudentGroup


class StudentGroupFormTests(TestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            email='teacher@example.com',
            password='test-password',
            first_name='Test',
            last_name='Teacher',
            is_teacher=True,
        )
        self.student_one = CustomUser.objects.create_user(
            email='amy@example.com',
            password='test-password',
            first_name='Amy',
            last_name='Chen',
        )
        self.student_two = CustomUser.objects.create_user(
            email='ben@example.com',
            password='test-password',
            first_name='Ben',
            last_name='Lin',
        )

    def test_student_choices_use_checkboxes_and_show_name_with_email(self):
        form = StudentGroupForm()

        self.assertEqual(
            form.fields['students'].widget.__class__.__name__,
            'CheckboxSelectMultiple',
        )
        self.assertEqual(
            form.fields['students'].label_from_instance(self.student_one),
            'Amy Chen — amy@example.com',
        )

    def test_students_can_be_deselected_and_reselected(self):
        group = StudentGroup.objects.create(
            name='Saturday Class',
            teacher=self.teacher,
        )
        group.students.set([self.student_one, self.student_two])

        deselect_form = StudentGroupForm(
            {'name': group.name, 'students': [self.student_two.pk]},
            instance=group,
        )
        self.assertTrue(deselect_form.is_valid(), deselect_form.errors)
        deselect_form.save()
        self.assertQuerySetEqual(
            group.students.order_by('pk'),
            [self.student_two],
        )

        reselect_form = StudentGroupForm(
            {
                'name': group.name,
                'students': [self.student_one.pk, self.student_two.pk],
            },
            instance=group,
        )
        self.assertTrue(reselect_form.is_valid(), reselect_form.errors)
        reselect_form.save()
        self.assertQuerySetEqual(
            group.students.order_by('pk'),
            [self.student_one, self.student_two],
        )
