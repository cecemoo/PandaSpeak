from django import forms

from course.models import StudentGroup
from .bingo_models import BingoGame
from .models import IdiomCategory, SentenceCategory, VocabularyCategory


class BingoGameForm(forms.ModelForm):
    category_key = forms.ChoiceField(required=False, label='Category (optional)')

    class Meta:
        model = BingoGame
        fields = [
            'title',
            'audience',
            'student_group',
            'game_mode',
            'content_type',
            'category_key',
            'level',
            'use_free_center',
            'adaptive_difficulty',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'audience': forms.Select(attrs={'class': 'form-select'}),
            'student_group': forms.Select(attrs={'class': 'form-select'}),
            'game_mode': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'use_free_center': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'adaptive_difficulty': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'audience': 'Who can play this Bingo?',
            'student_group': 'Student group (only required for One Student Group)',
            'game_mode': 'Bingo game mode',
            'content_type': 'Listening content',
            'use_free_center': 'Use FREE center square (3 x 3 and 5 x 5 cards)',
            'adaptive_difficulty': 'Adjust each student’s difficulty from recent Bingo performance',
            'is_active': 'Available to students',
        }
        help_texts = {
            'audience': (
                'All My Students means the unique students across every active group you created. '
                'All PandaSpeak Subscribers means all active student subscribers on PandaSpeak.'
            ),
            'game_mode': (
                'Listening Bingo plays an audio item and the student chooses the matching square. '
                'Make-Sentence Bingo asks the student to arrange shuffled Chinese characters into a sentence.'
            ),
            'content_type': 'Used for Listening Bingo. Make-Sentence Bingo always uses PandaSpeak sentences.',
            'level': 'Starting difficulty. Adaptive Bingo can move an individual student up or down later.',
            'adaptive_difficulty': 'Strong Bingo performance raises the next round; difficult rounds keep or lower the learning level.',
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        self.fields['student_group'].required = False
        self.fields['category_key'].widget.attrs.update({'class': 'form-select'})
        self.fields['category_key'].help_text = 'Choose a category to limit the Bingo to that topic, or leave All categories selected.'
        self.fields['category_key'].choices = [
            ('', 'All categories'),
            ('Vocabulary', [
                (f'vocabulary:{category.id}', category.category_name)
                for category in VocabularyCategory.objects.order_by('category_name')
            ]),
            ('Sentences', [
                (f'sentence:{category.id}', category.category_name)
                for category in SentenceCategory.objects.order_by('category_name')
            ]),
            ('Chinese Expressions', [
                (f'expression:{category.id}', category.category_name)
                for category in IdiomCategory.objects.order_by('category_name')
            ]),
        ]

        if teacher:
            self.fields['student_group'].queryset = StudentGroup.objects.filter(
                teacher=teacher,
                is_active=True,
            ).order_by('name')
        else:
            self.fields['student_group'].queryset = StudentGroup.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        audience = cleaned_data.get('audience')
        student_group = cleaned_data.get('student_group')
        game_mode = cleaned_data.get('game_mode')
        content_type = cleaned_data.get('content_type')
        category_key = cleaned_data.get('category_key') or ''

        if audience == 'group' and not student_group:
            self.add_error('student_group', 'Please choose a student group.')
        elif audience != 'group':
            cleaned_data['student_group'] = None

        if game_mode == 'make_sentence':
            content_type = 'sentence'
            cleaned_data['content_type'] = 'sentence'

        if category_key:
            expected_prefix = f'{content_type}:'
            if not category_key.startswith(expected_prefix):
                self.add_error('category_key', 'Please choose a category that matches the selected Bingo content.')

        return cleaned_data
