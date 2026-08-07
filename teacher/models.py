from django.db import models




class VocabularyCategory(models.Model):
    category_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.category_name



class Vocabulary(models.Model):
    word = models.CharField(max_length=100)
    pinyin = models.CharField(max_length=100, blank=True)
    english_translation = models.CharField(max_length=255, blank=True)
    meaning = models.TextField()
    example_sentence = models.TextField(blank=True)
    audio_file = models.FileField(upload_to='vocabulary_audio/', blank=True, null=True)
    category = models.ForeignKey(VocabularyCategory, on_delete=models.CASCADE, related_name='vocabularies', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    def __str__(self):
        return self.word
    



class Pronunciation(models.Model):
    symbol = models.CharField(max_length=5, blank=True)
    pinyin = models.CharField(max_length=10, blank=True)
    chinese_example = models.CharField(max_length=50, blank=True)
    pinyin_example = models.CharField(max_length=50, blank=True)
    english_example = models.CharField(max_length=50, blank=True)
    audio_file = models.FileField(upload_to='pronunciations/')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.symbol


class SentenceCategory(models.Model):
    category_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.category_name
       

class Sentence(models.Model):
    text = models.TextField()
    pinyin = models.CharField(max_length=255, blank=True)
    translation = models.TextField(blank=True)
    audio_file = models.FileField(upload_to='sentences/', blank=True, null=True)
    category = models.ForeignKey(SentenceCategory, on_delete=models.CASCADE, related_name='sentences', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.text[:50]  
    


class IdiomCategory(models.Model):
    category_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.category_name



class Idiom(models.Model):
    EXPRESSION_TYPES = [
        ("idiom", "Idiom"),
        ("proverb", "Proverb"),
        ("saying", "Saying"),
        ("phrase", "Phrase"),
        ("slang", "Slang"),
        ("quotation", "Quotation"),
    ]
    expression_type = models.CharField(max_length=30, choices=EXPRESSION_TYPES, default="idiom", verbose_name="Expression Type")
    idiom = models.CharField(max_length=100)
    pinyin = models.CharField(max_length=100, blank=True)
    english_translation = models.CharField(max_length=255, blank=True)
    meaning = models.TextField()
    example_scenario = models.TextField(blank=True)
    audio_scenario_file = models.FileField(upload_to='idiom_scenarios/', blank=True, null=True)
    category = models.ForeignKey(IdiomCategory, on_delete=models.CASCADE, related_name='idioms', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.idiom


class Tone(models.Model):

    TONE_CHOICES = [
        ('First Tone', 'First Tone'),
        ('Second Tone', 'Second Tone'),
        ('Third Tone', 'Third Tone'),
        ('Fourth Tone', 'Fourth Tone'),
    ]
    SYMBOL_CHOICES = [
        ('ˉ', '-'),
        ('ˊ', 'ˊ'),
        ('ˇ', 'ˇ'),
        ('ˋ', 'ˋ'),
    ]
    DESCRIPTION_CHOICES = [
        ('High Level', 'High Level'),
        ('Rising', 'Rising'),
        ('Falling-Rising', 'Falling-Rising'),
        ('Falling', 'Falling'),
    ]
    base_pinyin = models.CharField(max_length=20, blank=True)
    tone_name = models.CharField(max_length=50, choices=TONE_CHOICES)
    symbol = models.CharField(max_length=5, choices=SYMBOL_CHOICES)
    example = models.CharField(max_length=50)
    description = models.CharField(max_length=100, choices=DESCRIPTION_CHOICES)
    audio_file = models.FileField(upload_to='tones/')
