from django.conf import settings
from django.db import models


class BingoGame(models.Model):
    CONTENT_CHOICES = [
        ("vocabulary", "Vocabulary"),
        ("sentence", "Sentences"),
        ("expression", "Chinese Expressions"),
    ]
    CARD_SIZE_CHOICES = [
        (3, "3 x 3"),
        (4, "4 x 4"),
        (5, "5 x 5"),
    ]
    LEVEL_CHOICES = [
        ("level1", "Level I"),
        ("level2", "Level II"),
        ("level3", "Level III"),
        ("all", "All Levels"),
    ]

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_bingo_games",
    )
    title = models.CharField(max_length=200)
    student_group = models.ForeignKey(
        "course.StudentGroup",
        on_delete=models.CASCADE,
        related_name="bingo_games",
    )
    content_type = models.CharField(max_length=20, choices=CONTENT_CHOICES, default="vocabulary")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="level1")
    card_size = models.PositiveSmallIntegerField(choices=CARD_SIZE_CHOICES, default=5)
    use_free_center = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def required_item_count(self):
        total = self.card_size * self.card_size
        if self.use_free_center and self.card_size % 2 == 1:
            return total - 1
        return total

    class Meta:
        app_label = "teacher"
        ordering = ["-created_at"]


class BingoCard(models.Model):
    game = models.ForeignKey(BingoGame, on_delete=models.CASCADE, related_name="cards")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bingo_cards",
    )
    cells = models.JSONField(default=list)
    marked_positions = models.JSONField(default=list)
    has_bingo = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.game.title} - {self.student}"

    class Meta:
        app_label = "teacher"
        constraints = [
            models.UniqueConstraint(fields=["game", "student"], name="unique_bingo_card_per_student")
        ]
