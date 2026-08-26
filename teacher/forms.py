from django import forms
from django.forms import ModelForm
from account.models import CustomUser
from . models import Vocabulary, Sentence, Pronunciation, Idiom, Tone, LearningSurvey, SurveyQuestion
from student.models import LanguageTest, TestQuestion
from course.models import StudentGroup
from opencc import OpenCC

traditional_converter = OpenCC('s2tw')

def validate_traditional_chinese(value):
    if not value:
        return value
    converted = traditional_converter.convert(value)
    if converted != value:
        raise forms.ValidationError(
            f"Please use Traditional Chinese only. "
            f"Traditional Chinese suggested: {converted}"
        )
    return value





class UpdateUserForm(ModelForm):
    password = None
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name',]
        exclude = ['password1', 'password2',]


class VocabularyForm(ModelForm):
    def clean_word(self):
        return validate_traditional_chinese(
            self.cleaned_data.get('word')
        )
    def clean_example_sentence(self):
        return validate_traditional_chinese(
            self.cleaned_data.get('example_sentence')
        )
    class Meta:
        model = Vocabulary
        fields = '__all__'


class SentenceForm(ModelForm):
    def clean_text(self):
        return validate_traditional_chinese(
            self.cleaned_data.get('text')
        )
    class Meta:
        model = Sentence
        fields = '__all__'


class PronunciationForm(ModelForm):
    class Meta:
        model = Pronunciation
        fields = '__all__'


class IdiomForm(ModelForm):
    def clean_idiom(self):
        return validate_traditional_chinese(
            self.cleaned_data.get('idiom')
        )
    def clean_example_sentence(self):
        return validate_traditional_chinese(
            self.cleaned_data.get('example_sentence')
        )
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
            'student_group',
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
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher", None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields["student_group"].queryset = StudentGroup.objects.filter(
                teacher=teacher,
                is_active=True
            ).order_by("name")




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




class LearningSurveyForm(forms.ModelForm):
    class Meta:
        model = LearningSurvey
        fields = ["title", "description", "student_group", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter survey title"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Describe the purpose of this survey",
                "rows": 4
            }),
            "student_group": forms.Select(attrs={
                "class": "form-control"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }


class SurveyQuestionForm(forms.ModelForm):
    class Meta:
        model = SurveyQuestion
        fields = [
            "question_text",
            "question_type",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "order",
        ]
        widgets = {
            "question_text": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter survey question"
            }),
            "question_type": forms.Select(attrs={
                "class": "form-control"
            }),
            "option_a": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Option A"
            }),
            "option_b": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Option B"
            }),
            "option_c": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Option C"
            }),
            "option_d": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Option D"
            }),
            "order": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
        }