from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Perfil, Unidade, Setor


class UserRegistrationForm(UserCreationForm):
    """Formulário de registro de usuário"""
    email = forms.EmailField(required=True)
    nome = forms.CharField(max_length=200, required=True, label='Nome Completo')
    telefone = forms.CharField(max_length=20, required=False, label='Telefone')
    perfil_ref = forms.ModelChoiceField(
        queryset=Perfil.objects.filter(ativo=True),
        required=False,
        label='Perfil/Cargo',
        empty_label='Selecione um perfil'
    )
    unidade_ref = forms.ModelChoiceField(
        queryset=Unidade.objects.filter(ativo=True),
        required=False,
        label='Unidade/Departamento',
        empty_label='Selecione uma unidade'
    )
    setor_ref = forms.ModelChoiceField(
        queryset=Setor.objects.filter(ativo=True),
        required=False,
        label='Setor',
        empty_label='Selecione um setor'
    )

    class Meta:
        model = User
        fields = ('username', 'nome', 'email', 'telefone', 'perfil_ref', 'unidade_ref', 'setor_ref', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # Adicionar classes específicas para selects
        self.fields['perfil_ref'].widget.attrs['class'] = 'form-select'
        self.fields['unidade_ref'].widget.attrs['class'] = 'form-select'
        self.fields['setor_ref'].widget.attrs['class'] = 'form-select'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nome = self.cleaned_data['nome']
        user.telefone = self.cleaned_data.get('telefone', '')
        user.perfil_ref = self.cleaned_data.get('perfil_ref')
        user.unidade_ref = self.cleaned_data.get('unidade_ref')
        user.setor_ref = self.cleaned_data.get('setor_ref')
        
        # Definir first_name e last_name baseado no nome
        nome_parts = self.cleaned_data['nome'].split()
        if nome_parts:
            user.first_name = nome_parts[0]
            if len(nome_parts) > 1:
                user.last_name = ' '.join(nome_parts[1:])
        
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Formulário para atualizar perfil do usuário"""
    class Meta:
        model = User
        fields = [
            'nome', 'email', 'telefone', 'perfil_ref', 'unidade_ref', 'setor_ref', 'ativo', 'foto_perfil'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome Completo',
            'email': 'E-mail',
            'telefone': 'Telefone',
            'perfil_ref': 'Perfil/Cargo',
            'unidade_ref': 'Unidade/Departamento',
            'setor_ref': 'Setor',
            'ativo': 'Usuário Ativo',
            'foto_perfil': 'Foto do Perfil',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas registros ativos
        self.fields['perfil_ref'].queryset = Perfil.objects.filter(ativo=True)
        self.fields['unidade_ref'].queryset = Unidade.objects.filter(ativo=True)
        self.fields['setor_ref'].queryset = Setor.objects.filter(ativo=True)
        
        # Adicionar classes CSS
        self.fields['perfil_ref'].widget.attrs['class'] = 'form-select'
        self.fields['unidade_ref'].widget.attrs['class'] = 'form-select'
        self.fields['setor_ref'].widget.attrs['class'] = 'form-select'


class UserAdminForm(forms.ModelForm):
    """Formulário administrativo para usuários"""
    class Meta:
        model = User
        fields = [
            'username', 'nome', 'email', 'telefone', 'perfil_ref', 'unidade_ref', 'setor_ref',
            'departamento', 'cargo', 'perfil_id', 'unidade_id', 'setor_id',
            'ativo', 'is_staff', 'is_superuser', 'foto_perfil', 'is_manager'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'perfil_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidade_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'setor_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_manager': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar selects para relacionamentos
        self.fields['perfil_ref'].widget.attrs['class'] = 'form-select'
        self.fields['unidade_ref'].widget.attrs['class'] = 'form-select'
        self.fields['setor_ref'].widget.attrs['class'] = 'form-select'


class PerfilForm(forms.ModelForm):
    """Formulário para perfis"""
    class Meta:
        model = Perfil
        fields = ['nome', 'descricao', 'nivel_acesso', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nivel_acesso': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 4}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UnidadeForm(forms.ModelForm):
    """Formulário para unidades"""
    class Meta:
        model = Unidade
        fields = ['codigo', 'nome', 'descricao', 'responsavel', 'ativo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SetorForm(forms.ModelForm):
    """Formulário para setores"""
    class Meta:
        model = Setor
        fields = ['codigo', 'nome', 'descricao', 'unidade', 'responsavel', 'ativo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 