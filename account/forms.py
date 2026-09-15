from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from . models import CustomUser, PlacementQuestion
from django import forms
from teacher.models import VocabularyCategory, SentenceCategory, IdiomCategory

class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'is_teacher', 'news_emails']

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError('Please enter a valid email address.')
        domain = email.rsplit('@', 1)[-1]
        if '.' not in domain or domain.startswith('.') or domain.endswith('.'):
            raise forms.ValidationError('Please enter a valid email address.')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

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

class PlacementQuestionForm(forms.ModelForm):
    class Meta:
        model = PlacementQuestion
        fields = '__all__'

class PlacementResultEmailForm(forms.Form):
    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        }),
    )

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=160, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}))
