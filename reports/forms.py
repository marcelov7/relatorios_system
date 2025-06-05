from django import forms
from .models import Report, ReportCategory, ReportData


class ReportForm(forms.ModelForm):
    """Formulário para criar/editar relatórios"""
    
    class Meta:
        model = Report
        fields = [
            'title', 'description', 'category', 'start_date', 
            'end_date', 'is_public', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do relatório'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição do relatório'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ReportCategory.objects.all()


class ReportDataForm(forms.ModelForm):
    """Formulário para adicionar dados aos relatórios"""
    
    class Meta:
        model = ReportData
        fields = ['field_name', 'field_value', 'data_type']
        widgets = {
            'field_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do campo'
            }),
            'field_value': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Valor do campo'
            }),
            'data_type': forms.Select(attrs={'class': 'form-select'}),
        }


class ReportCategoryForm(forms.ModelForm):
    """Formulário para criar/editar categorias"""
    
    class Meta:
        model = ReportCategory
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da categoria'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da categoria'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
        }


class ReportFilterForm(forms.Form):
    """Formulário para filtrar relatórios"""
    
    category = forms.ModelChoiceField(
        queryset=ReportCategory.objects.all(),
        required=False,
        empty_label="Todas as categorias",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Report.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar relatórios...'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    ) 