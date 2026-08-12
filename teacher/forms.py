from django import forms
from django.forms import ModelForm
from account.models import CustomUser
from . models import Vocabulary, Sentence, Pronunciation, Idiom, Tone
from student.models import LanguageTest, TestQuestion




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


class LanguageTestForm(forms.ModelForm):
    class Meta:
        model = LanguageTest
        fields = [
            'title',
            'level',
            'test_type',
            'description',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'level': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'test_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }

class TestQuestionForm(forms.ModelForm):
    correct_choice = forms.ChoiceField(
        choices=[
            ('', 'Select correct answer'),
            ('A', 'Choice A'),
            ('B', 'Choice B'),
            ('C', 'Choice C'),
            ('D', 'Choice D'),
        ],
        required=False,
        label='Correct Answer',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = TestQuestion
        fields =[
            'question_type',
            'prompt',
            'choice_a',
            'choice_b',
            'choice_c',
            'choice_d',
            'correct_answer',
            'points',
            'order',
            'audio',
        ]
        widgets = {
            'question_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prompt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'correct_answer': forms.Textarea(attrs={
                'class': 'form-control'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }
        def save(self, commit=True):
            instance = super().save(commit=False)
            correct_choice = self.cleaned_data.get('correct_choice')
            if instance.question_type == 'listen_mc':
                if correct_choice == 'A':
                    instance.correct_answer = instance.choice_a
                elif correct_choice == 'B':
                    instance.correct_answer = instance.choice_b
                elif correct_choice == 'C':
                    instance.correct_answer = instance.choice_c
                elif correct_choice == 'D':
                    instance.correct_answer = instance.choice_d
            if commit:
                instance.save()
            return instance