from django.forms import ModelForm
from account.models import CustomUser
from . models import Vocabulary, Sentence, Pronunciation, Idiom, Tone


class UpdateUserForm(ModelForm):
    password = None
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name',]
        exclude = ['password1', 'password2',]


class VocabularyForm(ModelForm):
    class Meta:
        model = Vocabulary
        fields = '__all__'


class SentenceForm(ModelForm):
    class Meta:
        model = Sentence
        fields = '__all__'


class PronunciationForm(ModelForm):
    class Meta:
        model = Pronunciation
        fields = '__all__'


class IdiomForm(ModelForm):
    class Meta:
        model = Idiom
        fields = '__all__'
        labels = {
            'idiom': 'Chinese Expression',
        }


class ToneForm(ModelForm):
    class Meta:
        model = Tone
        fields = '__all__'