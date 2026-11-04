from django.db import models
from account.models import CustomUser
from course.models import StudentGroup
from django.conf import settings
from teacher.models import Vocabulary, Sentence, Idiom


class CulturalInsight(models.Model):
    LEVEL_CHOICES = [('level2', 'Level II'), ('level3', 'Level III')]
    CATEGORY_CHOICES = [
        ('daily', 'Daily Life & Etiquette'), ('festival', 'Festivals & Traditions'),
        ('food', 'Food & Dining'), ('language', 'Language & Communication'),
        ('society', 'Society & Relationships'), ('history', 'History & Heritage'),
        ('regional', 'Regional Culture'), ('modern', 'Modern Culture'),
    ]
    title = models.CharField(max_length=200)
    chinese_title = models.CharField(max_length=200, blank=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='daily')
    summary = models.CharField(max_length=350)
    content = models.TextField()
    useful_chinese = models.TextField(blank=True, help_text='Optional useful Traditional Chinese words or expressions.')
    did_you_know = models.TextField(blank=True)
    image = models.ImageField(upload_to='cultural_insights/', blank=True, null=True)
    audio = models.FileField(upload_to='cultural_insights/audio/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['level', 'order', 'title']

    def __str__(self):
        return f'{self.get_level_display()} - {self.title}'


class CulturalInsightUnlock(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cultural_insight_unlocks')
    insight = models.ForeignKey(CulturalInsight, on_delete=models.CASCADE, related_name='student_unlocks')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'insight'], name='unique_student_cultural_insight')]
        ordering = ['-unlocked_at']

    def __str__(self):
        return f'{self.student} - {self.insight}'


class CulturalInsightCompletion(models.Model):
    """Tracks completion of the built-in Cultural Insight lessons by stable lesson slug."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cultural_insight_completions')
    lesson_slug = models.SlugField(max_length=100)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'lesson_slug'], name='unique_student_cultural_lesson_completion')]
        ordering = ['-completed_at']

    def __str__(self):
        return f'{self.student} - {self.lesson_slug}'


class AchievementCelebration(models.Model):
    """Server-side record that an achievement has already been celebrated
    with the dashboard popup, so the popup fires once per achievement
    instead of relying on browser storage (which resets on a new
    browser/device or in private browsing). The sentinel name
    '__baseline__' marks that a student's pre-existing achievements were
    recorded without a popup when the tracking started for them."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievement_celebrations')
    achievement_name = models.CharField(max_length=100)
    celebrated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'achievement_name'], name='unique_student_achievement_celebration')]


class HistoryLessonCompletion(models.Model):
    """Tracks completion of built-in Chinese History lessons independently from culture lessons."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='history_lesson_completions')
    lesson_slug = models.SlugField(max_length=100)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'lesson_slug'], name='unique_student_history_lesson_completion')]
        ordering = ['-completed_at']

    def __str__(self):
        return f'{self.student} - {self.lesson_slug}'


class AIConversationUsage(models.Model):
    KIND_CHOICES = [('reply', 'AI Reply'), ('speech', 'AI Speech')]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversation_usage')
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    model_name = models.CharField(max_length=100, blank=True)
    input_units = models.PositiveIntegerField(default=0)
    output_units = models.PositiveIntegerField(default=0)
    estimated_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    cached = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['student', 'created_at']), models.Index(fields=['kind', 'created_at'])]


class AICachedSpeech(models.Model):
    cache_key = models.CharField(max_length=64, unique=True)
    voice = models.CharField(max_length=20)
    text = models.TextField()
    audio = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)


# Every test is timed; a test without an instructor-set limit uses this default.
DEFAULT_TEST_TIME_LIMIT_MINUTES = 30


class LanguageTest(models.Model):
    TEST_TYPES = [('speaking', 'Speaking'), ('listening', 'Listening'), ('mixed', 'Speaking & Listening')]
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='language_tests', limit_choices_to={'is_teacher': True}, null=True, blank=True)
    level = models.CharField(max_length=50)
    test_type = models.CharField(max_length=20, choices=TEST_TYPES)
    description = models.TextField(blank=True)
    available_from = models.DateTimeField(blank=True, null=True)
    available_until = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, help_text='Optional time limit per student in minutes')
    student_group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='language_tests')
    assigned_students = models.ManyToManyField(CustomUser, blank=True, related_name='assigned_tests')
    is_manager_test = models.BooleanField(default=False)
    def __str__(self): return self.title

class AssessmentRequest(models.Model):
    """A student's request for a comprehensive assessment test.

    Assessments are generated instantly from the level's materials.
    Listening-only tests never create one of these; a generated speaking
    or speaking & listening test records one already fulfilled, linked to
    the test (fulfilled_test) — that link is what makes the test show up
    in the manager grading pages, where a manager scores the speaking
    part. Only when a level lacks the material for instant generation is
    a request left pending: the PandaSpeak team then prepares the test by
    hand from the manager dashboard (assigned to the student via
    LanguageTest.assigned_students) and the request is marked fulfilled
    when that test is published.
    """
    LEVEL_CHOICES = [('level1', 'Level I'), ('level2', 'Level II'), ('level3', 'Level III')]
    TEST_TYPE_CHOICES = [('speaking', 'Speaking'), ('mixed', 'Speaking & Listening')]
    STATUS_CHOICES = [('pending', 'Pending'), ('fulfilled', 'Fulfilled'), ('cancelled', 'Cancelled')]
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assessment_requests')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fulfilled_test = models.ForeignKey(LanguageTest, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessment_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.student.email} - {self.get_level_display()} {self.get_test_type_display()} ({self.get_status_display()})"

class TestQuestion(models.Model):
    QUESTION_TYPES = [('listen_mc', 'Listening - Multiple Choice'), ('speak_read', 'Speaking - Read Aloud')]
    test = models.ForeignKey(LanguageTest, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    prompt = models.TextField()
    choice_a = models.CharField(max_length=500, blank=True, null=True); choice_b = models.CharField(max_length=500, blank=True, null=True); choice_c = models.CharField(max_length=500, blank=True, null=True); choice_d = models.CharField(max_length=500, blank=True, null=True)
    audio = models.FileField(upload_to='test_audio/', blank=True, null=True)
    correct_answer = models.TextField(blank=True, null=True)
    points = models.PositiveIntegerField(default=1); order = models.PositiveIntegerField(default=1)
    def __str__(self): return f"{self.test.title} - Question {self.order}"

class TimedTestAttempt(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey(LanguageTest, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    draft_answers = models.JSONField(default=dict, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    auto_submitted = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'test'], name='unique_timed_test_attempt')]

class StudentTestSubmission(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE); test = models.ForeignKey(LanguageTest, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True); listening_score = models.FloatField(blank=True, null=True); speaking_score = models.FloatField(blank=True, null=True); total_score = models.FloatField(blank=True, null=True); is_graded = models.BooleanField(default=False)
    def __str__(self): return f"{self.student.email} - {self.test.title}"

class StudentListeningAnswer(models.Model):
    submission = models.ForeignKey(StudentTestSubmission, on_delete=models.CASCADE); question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE); answer = models.TextField(); is_correct = models.BooleanField(default=False); score = models.FloatField(default=0)
    def __str__(self): return f"{self.submission.student.email} - {self.question.test.title} - Question {self.question.order}"

class StudentSpeakingAnswer(models.Model):
    submission = models.ForeignKey(StudentTestSubmission, on_delete=models.CASCADE, related_name='speaking_answers', blank=True, null=True)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE); question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE); submitted_at = models.DateTimeField(auto_now_add=True); email_sent = models.BooleanField(default=False); email_sent_at = models.DateTimeField(blank=True, null=True); score = models.FloatField(blank=True, null=True); teacher_feedback = models.TextField(blank=True, null=True); audio_file = models.FileField(upload_to='speaking_answers/', blank=True, null=True)
    def __str__(self): return f"{self.student.email} - {self.question.test.title} - Question {self.question.order}"

class Favorite(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, null=True, blank=True); sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, null=True, blank=True); idiom = models.ForeignKey(Idiom, on_delete=models.CASCADE, null=True, blank=True); created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.student} - Favorite"

class LearnedItem(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learned_items')
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, null=True, blank=True); sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, null=True, blank=True); idiom = models.ForeignKey(Idiom, on_delete=models.CASCADE, null=True, blank=True); learned_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.student} - Learned Item"

class PersonalFlashcard(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personal_flashcards')
    source_vocabulary = models.ForeignKey(Vocabulary, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_flashcards'); source_sentence = models.ForeignKey(Sentence, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_flashcards'); source_idiom = models.ForeignKey(Idiom, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_flashcards')
    front = models.CharField(max_length=300); pinyin = models.CharField(max_length=300, blank=True); meaning = models.CharField(max_length=500); example = models.TextField(blank=True); notes = models.TextField(blank=True); created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"{self.student} - {self.front}"
