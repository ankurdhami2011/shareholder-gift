from django import forms
from .models import Branch


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['branch_code', 'branch_name', 'is_active']
        widgets = {
            'branch_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch code'
            }),
            'branch_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch name'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_branch_code(self):
        branch_code = self.cleaned_data['branch_code'].strip().upper()

        qs = Branch.objects.filter(branch_code__iexact=branch_code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Branch code already exists.')

        return branch_code

    def clean_branch_name(self):
        branch_name = self.cleaned_data['branch_name'].strip()

        qs = Branch.objects.filter(branch_name__iexact=branch_name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Branch name already exists.')

        return branch_name