from django import forms

from course.models import StudentGroup
from .bingo_models import BingoGame


class BingoGameForm(forms.ModelForm):
    class Meta:
        model = BingoGame
        fields = [
            'title',
            'student_group',
            'content_type',
            'level',
            'card_size',
            'use_free_center',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'student_group': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'card_size': forms.Select(attrs={'class': 'form-select'}),
            'use_free_center': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'use_free_center': 'Use FREE center square (odd-sized cards only)',
            'is_active': 'Available to students',
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['student_group'].queryset = StudentGroup.objects.filter(
                teacher=teacher,
                is_active=True,
            ).order_by('name')
        else:
            self.fields['student_group'].queryset = StudentGroup.objects.none()
