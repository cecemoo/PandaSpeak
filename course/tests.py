from django.test import TestCase
from django.urls import reverse

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

    def test_student_choices_exclude_managers_admins_and_teachers(self):
        manager = CustomUser.objects.create_user(
            email='manager@example.com',
            password='test-password',
            first_name='Site',
            last_name='Manager',
            is_staff=True,
        )
        admin = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='test-password',
            first_name='Site',
            last_name='Admin',
        )
        other_teacher = CustomUser.objects.create_user(
            email='other-teacher@example.com',
            password='test-password',
            first_name='Other',
            last_name='Teacher',
            is_teacher=True,
        )

        available_students = StudentGroupForm().fields['students'].queryset

        self.assertIn(self.student_one, available_students)
        self.assertIn(self.student_two, available_students)
        self.assertNotIn(manager, available_students)
        self.assertNotIn(admin, available_students)
        self.assertNotIn(self.teacher, available_students)
        self.assertNotIn(other_teacher, available_students)

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

    def test_create_page_places_buttons_after_the_student_list(self):
        self.client.force_login(self.teacher)

        response = self.client.get(reverse('create_student_group'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student-checkbox-list')
        content = response.content.decode()
        self.assertLess(
            content.index('amy@example.com'),
            content.index('Create Group'),
        )
