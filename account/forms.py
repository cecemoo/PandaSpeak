from django.contrib.auth.forms import UserCreationForm
from . models import CustomUser
from django import forms
from teacher.models import VocabularyCategory, SentenceCategory, IdiomCategory

class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'is_teacher']
       

class AddVocabCategoryForm(forms.ModelForm):
    class Meta:
        model = VocabularyCategory
        fields = '__all__'

class AddSentenceCategoryForm(forms.ModelForm):
    class Meta:
        model = SentenceCategory
        fields = '__all__'

class AddIdiomCategoryForm(forms.ModelForm):
    class Meta:
        model = IdiomCategory
        fields = '__all__'