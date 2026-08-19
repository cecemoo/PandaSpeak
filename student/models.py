from django.db import models
from account.models import CustomUser
from course.models import StudentGroup



class LanguageTest(models.Model):
    TEST_TYPES = [
        ('speaking', 'Speaking'),
        ('listening', 'Listening'),
        ('mixed', 'Speaking & Listening'),
    ]
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='language_tests', limit_choices_to={'is_teacher': True}, null=True, blank=True)
    level = models.CharField(max_length=50)
    test_type = models.CharField(max_length=20, choices=TEST_TYPES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)
    student_group = models.ForeignKey(
        StudentGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='language_tests'
    )

    def __str__(self):
        return self.title


class TestQuestion(models.Model):
    QUESTION_TYPES = [
        ('listen_mc', 'Listening - Multiple Choice'),
        ('speak_read', 'Speaking - Read Aloud'),
       
    ]
    test = models.ForeignKey(LanguageTest, on_delete=models.CASCADE, related_name = 'questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    prompt = models.TextField()
    choice_a = models.CharField(max_length=500, blank=True, null=True)
    choice_b = models.CharField(max_length=500, blank=True, null=True)
    choice_c = models.CharField(max_length=500, blank=True, null=True)
    choice_d = models.CharField(max_length=500, blank=True, null=True)
    audio = models.FileField(upload_to='test_audio/', blank=True, null=True)
    correct_answer = models.TextField(blank=True, null=True)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.test.title} - Question {self.order}"


class StudentSpeakingAnswer(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    teacher_feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.email} - {self.question.test.title} - Question {self.question.order}"



class StudentTestSubmission(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey(LanguageTest, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    listening_score = models.FloatField(blank=True, null=True)
    speaking_score = models.FloatField(blank=True, null=True)
    total_score = models.FloatField(blank=True, null=True)
    is_graded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.email} - {self.test.title}"



class StudentListeningAnswer(models.Model):
    submission = models.ForeignKey(StudentTestSubmission, on_delete=models.CASCADE)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.submission.student.email} - {self.question.test.title} - Question {self.question.order}"