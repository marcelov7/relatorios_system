from django import forms
from .models import Report, ReportCategory, ReportData, ReportImage, ReportUpdate, ReportUpdateImage
from locations.models import Local, Equipamento
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportForm(forms.ModelForm):
    """Formulário para criar/editar relatórios com dropdowns de Local e Equipamento"""
    
    class Meta:
        model = Report
        fields = [
            'titulo', 'descricao', 'local', 'equipamento', 'atribuido_para',
            'data_ocorrencia', 'status', 'prioridade', 'progresso', 'editavel', 'imagem_principal'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do relatório'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição do relatório'
            }),
            'local': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_local'
            }),
            'equipamento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_equipamento'
            }),
            'atribuido_para': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_atribuido_para'
            }),
            'data_ocorrencia': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'progresso': forms.NumberInput(attrs={
                'type': 'range',
                'class': 'form-range',
                'min': 0,
                'max': 100,
                'step': 1,
                'id': 'id_progresso'
            }),
            'editavel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagem_principal': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar querysets para os dropdowns
        self.fields['local'].queryset = Local.objects.filter(status='ativo').order_by('nome')
        self.fields['local'].empty_label = "Selecione um local"
        
        self.fields['equipamento'].queryset = Equipamento.objects.filter(ativo=True).order_by('nome')
        self.fields['equipamento'].empty_label = "Selecione um equipamento"
        
        self.fields['atribuido_para'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'username')
        self.fields['atribuido_para'].empty_label = "Não atribuído (autor responsável)"
        
        # Adicionar labels personalizadas
        self.fields['titulo'].label = 'Título'
        self.fields['descricao'].label = 'Descrição'
        self.fields['local'].label = 'Local'
        self.fields['equipamento'].label = 'Equipamento'
        self.fields['atribuido_para'].label = 'Atribuir Para'
        self.fields['data_ocorrencia'].label = 'Data da Ocorrência'
        self.fields['status'].label = 'Status'
        self.fields['prioridade'].label = 'Prioridade'
        self.fields['progresso'].label = 'Progresso (%)'
        self.fields['editavel'].label = 'Editável'
        self.fields['imagem_principal'].label = 'Imagem Principal'


class ReportImageForm(forms.ModelForm):
    """Formulário para upload de imagens adicionais"""
    class Meta:
        model = ReportImage
        fields = ['imagem', 'descricao']
        widgets = {
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Antes da manutenção, Problema identificado, Solução aplicada...'
            })
        }


# Formset para múltiplas imagens
ReportImageFormSet = forms.inlineformset_factory(
    Report, 
    ReportImage, 
    form=ReportImageForm,
    extra=3,  # 3 campos extras por padrão
    can_delete=True,
    fields=['imagem', 'descricao']
)


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
    """Formulário para filtrar relatórios com filtros avançados"""
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Report.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Status'
    )
    
    prioridade = forms.ChoiceField(
        choices=[('', 'Todas as prioridades')] + Report.PRIORIDADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Prioridade'
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título ou descrição...'
        }),
        label='Buscar'
    )
    
    # Filtros por data melhorados
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Data inicial'
        }),
        label='De'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Data final'
        }),
        label='Até'
    )
    
    # Filtro por período predefinido
    PERIODO_CHOICES = [
        ('', 'Período personalizado'),
        ('hoje', 'Hoje'),
        ('ontem', 'Ontem'),
        ('ultima_semana', 'Última semana'),
        ('ultimo_mes', 'Último mês'),
        ('ultimos_3_meses', 'Últimos 3 meses'),
        ('este_ano', 'Este ano'),
    ]
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_periodo'
        }),
        label='Período'
    )
    
    local = forms.ModelChoiceField(
        queryset=Local.objects.filter(status='ativo').order_by('nome'),
        required=False,
        empty_label='Todos os locais',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Local'
    )
    
    equipamento = forms.ModelChoiceField(
        queryset=Equipamento.objects.filter(ativo=True).order_by('nome'),
        required=False,
        empty_label='Todos os equipamentos',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Equipamento'
    )
    
    # Filtro por usuário (para administradores)
    usuario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do usuário...'
        }),
        label='Usuário'
    )
    
    # Ordenação
    ORDENACAO_CHOICES = [
        ('-data_criacao', 'Mais recentes primeiro'),
        ('data_criacao', 'Mais antigos primeiro'),
        ('-data_ocorrencia', 'Data ocorrência (recente)'),
        ('data_ocorrencia', 'Data ocorrência (antiga)'),
        ('titulo', 'Título (A-Z)'),
        ('-titulo', 'Título (Z-A)'),
        ('status', 'Status'),
        ('-prioridade', 'Prioridade (alta primeiro)'),
    ]
    
    ordenar_por = forms.ChoiceField(
        choices=ORDENACAO_CHOICES,
        required=False,
        initial='-data_criacao',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Ordenar por'
    )


class ReportUpdateForm(forms.ModelForm):
    """Formulário para atualizar status e progresso do relatório"""
    
    class Meta:
        model = ReportUpdate
        fields = ['progresso_novo', 'descricao_atualizacao']
        widgets = {
            'progresso_novo': forms.NumberInput(attrs={
                'type': 'range',
                'class': 'form-range',
                'min': 0,
                'max': 100,
                'step': 1,
                'id': 'id_progresso_novo'
            }),
            'descricao_atualizacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva o que foi feito nesta atualização...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.report = kwargs.pop('report', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.report:
            # Definir valor mínimo como o progresso atual
            self.fields['progresso_novo'].widget.attrs['min'] = self.report.progresso
            self.fields['progresso_novo'].initial = self.report.progresso
            
        self.fields['progresso_novo'].label = 'Novo Progresso (%)'
        self.fields['descricao_atualizacao'].label = 'Descrição da Atualização'
    
    def clean_progresso_novo(self):
        progresso = self.cleaned_data.get('progresso_novo')
        if self.report and progresso < self.report.progresso:
            raise forms.ValidationError(
                f'O progresso não pode ser menor que o atual ({self.report.progresso}%)'
            )
        return progresso


class ReportUpdateImageForm(forms.ModelForm):
    """Formulário para imagens da atualização"""
    
    class Meta:
        model = ReportUpdateImage
        fields = ['imagem', 'descricao']
        widgets = {
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da imagem (opcional)'
            })
        }


# Formset para múltiplas imagens da atualização
ReportUpdateImageFormSet = forms.inlineformset_factory(
    ReportUpdate,
    ReportUpdateImage,
    form=ReportUpdateImageForm,
    extra=2,  # 2 campos extras por padrão
    can_delete=False,
    fields=['imagem', 'descricao']
) 