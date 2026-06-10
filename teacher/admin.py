from django.contrib import admin
from .models import Vocabulary, Pronunciation, Sentence, Idiom, VocabularyCategory, SentenceCategory, IdiomCategory

# Register your models here.

admin.site.register(Vocabulary)
admin.site.register(Pronunciation)
admin.site.register(Sentence)
admin.site.register(Idiom)
admin.site.register(VocabularyCategory)
admin.site.register(SentenceCategory)
admin.site.register(IdiomCategory)