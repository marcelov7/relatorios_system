from django import forms
from .models import Local, Equipamento, Motor
from django.contrib.auth import get_user_model

User = get_user_model()


class LocalForm(forms.ModelForm):
    """Formulário para criar/editar locais - versão simplificada"""
    
    class Meta:
        model = Local
        fields = [
            'nome', 'codigo', 'tipo', 'endereco', 'status'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do local'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único do local'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Endereço completo'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar labels
        self.fields['nome'].label = 'Nome do Local'
        self.fields['codigo'].label = 'Código'
        self.fields['tipo'].label = 'Tipo de Local'
        self.fields['endereco'].label = 'Endereço'
        self.fields['status'].label = 'Status'


class EquipamentoForm(forms.ModelForm):
    """Formulário para criar/editar equipamentos - baseado na estrutura da tabela"""
    
    class Meta:
        model = Equipamento
        fields = [
            'local', 'nome', 'codigo', 'descricao', 'tipo', 'fabricante', 
            'modelo', 'numero_serie', 'data_instalacao', 'status_operacional', 'ativo'
        ]
        widgets = {
            'local': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do equipamento'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código do equipamento'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do equipamento'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fabricante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fabricante do equipamento'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de série'
            }),
            'data_instalacao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status_operacional': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar labels
        self.fields['local'].label = 'Local'
        self.fields['nome'].label = 'Nome'
        self.fields['codigo'].label = 'Código'
        self.fields['descricao'].label = 'Descrição'
        self.fields['tipo'].label = 'Tipo'
        self.fields['fabricante'].label = 'Fabricante'
        self.fields['modelo'].label = 'Modelo'
        self.fields['numero_serie'].label = 'Número de Série'
        self.fields['data_instalacao'].label = 'Data de Instalação'
        self.fields['status_operacional'].label = 'Status Operacional'
        self.fields['ativo'].label = 'Ativo'


class LocalFilterForm(forms.Form):
    """Formulário para filtrar locais"""
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Local.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Local.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar locais...'
        })
    )


class EquipamentoFilterForm(forms.Form):
    """Formulário para filtrar equipamentos"""
    
    local = forms.ModelChoiceField(
        queryset=Local.objects.all(),
        required=False,
        empty_label='Todos os locais',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Equipamento.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status_operacional = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Equipamento.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar equipamentos...'
        })
    )


class MotorForm(forms.ModelForm):
    """Formulário para criar/editar motores elétricos"""
    
    class Meta:
        model = Motor
        fields = [
            'local', 'nome', 'codigo', 'descricao', 'tipo', 
            'potencia', 'voltagem', 'corrente', 'rpm',
            'fabricante', 'modelo', 'numero_serie', 'data_instalacao',
            'status_operacional', 'responsavel', 'ativo'
        ]
        widgets = {
            'local': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do motor'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único do motor'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada do motor'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'potencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Potência em CV'
            }),
            'voltagem': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Tensão em Volts'
            }),
            'corrente': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Corrente em Ampères'
            }),
            'rpm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rotações por minuto'
            }),
            'fabricante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fabricante do motor'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo do motor'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de série único'
            }),
            'data_instalacao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status_operacional': forms.Select(attrs={'class': 'form-select'}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Carregar apenas usuários ativos
        self.fields['responsavel'].queryset = User.objects.filter(is_active=True)
        self.fields['responsavel'].empty_label = 'Selecione um responsável'


class MotorFilterForm(forms.Form):
    """Formulário para filtrar motores"""
    
    local = forms.ModelChoiceField(
        queryset=Local.objects.all(),
        required=False,
        empty_label='Todos os locais',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Motor.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status_operacional = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Motor.STATUS_OPERACIONAL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fabricante = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filtrar por fabricante...'
        })
    )
    
    potencia_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Potência mín. (CV)',
            'step': '0.1'
        })
    )
    
    potencia_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Potência máx. (CV)',
            'step': '0.1'
        })
    )
    
    corrente_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Corrente mín. (A)',
            'step': '0.1'
        })
    )
    
    corrente_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Corrente máx. (A)',
            'step': '0.1'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar motores...'
        })
    ) 