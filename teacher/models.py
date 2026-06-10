from django.db import models




class VocabularyCategory(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title



class Vocabulary(models.Model):
    word = models.CharField(max_length=100)
    pinyin = models.CharField(max_length=100, blank=True)
    meaning = models.TextField()
    example_sentence = models.TextField(blank=True)
    audio_file = models.FileField(upload_to='vocabulary_audio/', blank=True, null=True)
    category = models.ForeignKey(VocabularyCategory, on_delete=models.CASCADE, related_name='vocabularies', blank=True, null=True)
    def __str__(self):
        return self.word
    



class Pronunciation(models.Model):
    word = models.CharField(max_length=100)
    pinyin = models.CharField(max_length=100, blank=True)
    audio_file = models.FileField(upload_to='pronunciations/')

    def __str__(self):
        return self.word


class SentenceCategory(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
       

class Sentence(models.Model):
    text = models.TextField()
    translation = models.TextField(blank=True)
    audio_file = models.FileField(upload_to='sentences/', blank=True, null=True)
    category = models.ForeignKey(SentenceCategory, on_delete=models.CASCADE, related_name='sentences', blank=True, null=True)

    def __str__(self):
        return self.text[:50]  
    


class IdiomCategory(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title



class Idiom(models.Model):
    idiom = models.CharField(max_length=100)
    pinyin = models.CharField(max_length=100, blank=True)
    meaning = models.TextField()
    example_scenario = models.TextField(blank=True)
    audio_scenario_file = models.FileField(upload_to='idiom_scenarios/', blank=True, null=True)
    category = models.ForeignKey(IdiomCategory, on_delete=models.CASCADE, related_name='idioms', blank=True, null=True)

    def __str__(self):
        return self.idiom

