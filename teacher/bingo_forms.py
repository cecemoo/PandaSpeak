from django import forms

from course.models import StudentGroup
from .bingo_models import BingoGame


class BingoGameForm(forms.ModelForm):
    class Meta:
        model = BingoGame
        fields = [
            'title',
            'audience',
            'student_group',
            'game_mode',
            'content_type',
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

        if audience == 'group' and not student_group:
            self.add_error('student_group', 'Please choose a student group.')
        elif audience != 'group':
            cleaned_data['student_group'] = None

        if game_mode == 'make_sentence':
            cleaned_data['content_type'] = 'sentence'

        return cleaned_data
