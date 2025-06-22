from django.contrib.auth.models import AbstractUser
from django.db import models


class Perfil(models.Model):
    """Modelo para perfis/cargos de usuário"""
    nome = models.CharField(max_length=100, verbose_name='Nome do Perfil')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    nivel_acesso = models.IntegerField(default=1, verbose_name='Nível de Acesso', 
                                      help_text='1=Baixo, 2=Médio, 3=Alto, 4=Total')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['nivel_acesso', 'nome']

    def __str__(self):
        return self.nome


class Unidade(models.Model):
    """Modelo para unidades/departamentos"""
    nome = models.CharField(max_length=100, verbose_name='Nome da Unidade')
    codigo = models.CharField(max_length=10, unique=True, verbose_name='Código')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    responsavel = models.CharField(max_length=100, blank=True, verbose_name='Responsável')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'
        ordering = ['nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Setor(models.Model):
    """Modelo para setores de trabalho"""
    SETORES_CHOICES = [
        ('M_ELETRICA', 'M. Elétrica'),
        ('M_MECANICA', 'M. Mecânica'),
        ('REFRIGERACAO', 'Refrigeração'),
        ('PRODUCAO', 'Produção'),
        ('C_QUALIDADE', 'C. Qualidade'),
        ('TERCEIRO', 'Terceiro'),
    ]
    
    nome = models.CharField(max_length=100, choices=SETORES_CHOICES, verbose_name='Nome do Setor')
    codigo = models.CharField(max_length=15, unique=True, verbose_name='Código')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='setores', 
                               verbose_name='Unidade', null=True, blank=True)
    responsavel = models.CharField(max_length=100, blank=True, verbose_name='Responsável')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'
        ordering = ['nome']

    def __str__(self):
        return f"{self.codigo} - {self.get_nome_display()}"


class User(AbstractUser):
    """Modelo de usuário extendido baseado na estrutura da tabela"""
    
    # Campo nome (pode usar first_name + last_name do AbstractUser)
    nome = models.CharField(max_length=200, blank=True, default='', verbose_name='Nome Completo', 
                           help_text='Nome completo do usuário')
    
    # Campo email já existe no AbstractUser, mas vamos garantir que seja único
    email = models.EmailField(unique=True, verbose_name='E-mail')
    
    # Campo senha já existe no AbstractUser como password
    senha = models.CharField(max_length=255, blank=True, default='', verbose_name='Senha Hash', 
                            help_text='Hash da senha (não modificar diretamente)')
    
    # Relacionamentos com as tabelas de referência
    perfil_ref = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Perfil', related_name='usuarios')
    unidade_ref = models.ForeignKey(Unidade, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Unidade', related_name='usuarios')
    setor_ref = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='Setor', related_name='usuarios')
    
    # Campos de compatibilidade (manter para não quebrar código existente)
    perfil_id = models.IntegerField(null=True, blank=True, verbose_name='ID do Perfil (Legacy)',
                                   help_text='Campo de compatibilidade - use o campo "perfil_ref"')
    unidade_id = models.IntegerField(null=True, blank=True, verbose_name='ID da Unidade (Legacy)',
                                    help_text='Campo de compatibilidade - use o campo "unidade_ref"')
    setor_id = models.IntegerField(null=True, blank=True, verbose_name='ID do Setor (Legacy)',
                                  help_text='Campo de compatibilidade - use o campo "setor_ref"')
    
    # Campo ativo (similar ao is_active do AbstractUser)
    ativo = models.BooleanField(default=True, verbose_name='Ativo',
                               help_text='Indica se o usuário está ativo no sistema')
    
    # Campo password_hash - para compatibilidade
    password_hash = models.CharField(max_length=255, blank=True, default='', verbose_name='Password Hash',
                                    help_text='Hash da senha para compatibilidade')
    
    # Campos de timestamp
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    # Campos adicionais para funcionalidade
    telefone = models.CharField(max_length=20, blank=True, default='', verbose_name='Telefone')
    departamento = models.CharField(max_length=100, blank=True, default='', verbose_name='Departamento')
    cargo = models.CharField(max_length=100, blank=True, default='', verbose_name='Cargo')
    foto_perfil = models.ImageField(upload_to='perfil/', blank=True, null=True, verbose_name='Foto do Perfil')
    is_manager = models.BooleanField(default=False, verbose_name='É Gerente?')

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']
        db_table = 'auth_user'  # Manter compatibilidade com tabela existente

    def __str__(self):
        return self.nome or self.get_full_name() or self.username

    def get_full_name(self):
        """Retorna o nome completo do usuário"""
        if self.nome:
            return self.nome
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_perfil_display(self):
        """Retorna o nome do perfil ou ID legacy"""
        if self.perfil_ref:
            return self.perfil_ref.nome
        elif self.perfil_id:
            perfil_map = {1: 'Super Admin', 2: 'Admin', 3: 'Manager', 4: 'Usuário'}
            return perfil_map.get(self.perfil_id, f'Perfil {self.perfil_id}')
        return 'Não definido'
    
    def get_unidade_display(self):
        """Retorna o nome da unidade ou ID legacy"""
        if self.unidade_ref:
            return str(self.unidade_ref)
        elif self.unidade_id:
            return f'Unidade {self.unidade_id}'
        return 'Não definido'
    
    def get_setor_display(self):
        """Retorna o nome do setor ou ID legacy"""
        if self.setor_ref:
            return str(self.setor_ref)
        elif self.setor_id:
            return f'Setor {self.setor_id}'
        return 'Não definido'
    
    # Propriedades para compatibilidade
    @property
    def perfil(self):
        """Propriedade para compatibilidade com código existente"""
        return self.perfil_ref
    
    @perfil.setter
    def perfil(self, value):
        """Setter para compatibilidade com código existente"""
        self.perfil_ref = value
    
    @property
    def unidade(self):
        """Propriedade para compatibilidade com código existente"""
        return self.unidade_ref
    
    @unidade.setter
    def unidade(self, value):
        """Setter para compatibilidade com código existente"""
        self.unidade_ref = value
    
    @property
    def setor(self):
        """Propriedade para compatibilidade com código existente"""
        return self.setor_ref
    
    @setor.setter
    def setor(self, value):
        """Setter para compatibilidade com código existente"""
        self.setor_ref = value
    
    def save(self, *args, **kwargs):
        """Override save para sincronizar campos"""
        # Sincronizar nome com first_name + last_name se nome estiver vazio
        if not self.nome and (self.first_name or self.last_name):
            self.nome = f"{self.first_name} {self.last_name}".strip()
        
        # Sincronizar ativo com is_active
        self.is_active = self.ativo
        
        # Sincronizar password_hash com password se necessário
        if self.password and not self.password_hash:
            self.password_hash = self.password
        
        # Sincronizar senha com password se necessário
        if self.password and not self.senha:
            self.senha = self.password
        
        # Sincronizar IDs legacy com relacionamentos
        if self.perfil_ref and not self.perfil_id:
            self.perfil_id = self.perfil_ref.id
        if self.unidade_ref and not self.unidade_id:
            self.unidade_id = self.unidade_ref.id
        if self.setor_ref and not self.setor_id:
            self.setor_id = self.setor_ref.id
        
        super().save(*args, **kwargs) 