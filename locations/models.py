from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

User = get_user_model()


class Local(models.Model):
    """Modelo para locais da empresa"""
    
    TIPO_CHOICES = [
        ('escritorio', 'Escritório'),
        ('fabrica', 'Fábrica'),
        ('deposito', 'Depósito'),
        ('loja', 'Loja'),
        ('filial', 'Filial'),
        ('matriz', 'Matriz'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('manutencao', 'Em Manutenção'),
        ('desativado', 'Desativado'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name='Nome do Local')
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')
    endereco = models.TextField(blank=True, verbose_name='Endereço')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado (UF)')
    cep = models.CharField(max_length=10, verbose_name='CEP')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    responsavel = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Responsável',
        related_name='locais_responsavel'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name='Status')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    
    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'
        ordering = ['nome']
        
    def __str__(self):
        return f"{self.nome} ({self.codigo})"
    
    def get_absolute_url(self):
        return reverse('locations:local_detail', kwargs={'pk': self.pk})
    
    def get_status_color(self):
        colors = {
            'ativo': 'success',
            'inativo': 'secondary',
            'manutencao': 'warning',
            'desativado': 'danger',
        }
        return colors.get(self.status, 'secondary')
    
    def get_equipamentos_count(self):
        return self.equipamentos.count()


class Equipamento(models.Model):
    """Modelo para equipamentos de cada local"""
    
    TIPO_CHOICES = [
        ('computador', 'Computador'),
        ('impressora', 'Impressora'),
        ('servidor', 'Servidor'),
        ('roteador', 'Roteador'),
        ('switch', 'Switch'),
        ('telefone', 'Telefone'),
        ('monitor', 'Monitor'),
        ('projetor', 'Projetor'),
        ('scanner', 'Scanner'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('operando', 'Operando'),
        ('manutencao', 'Manutenção'),
        ('inativo', 'Inativo'),
        ('almoxarifado', 'Almoxarifado'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    local = models.ForeignKey(
        Local, 
        on_delete=models.CASCADE, 
        related_name='equipamentos', 
        verbose_name='Local'
    )
    nome = models.CharField(max_length=100, verbose_name='Nome')
    codigo = models.CharField(max_length=50, verbose_name='Código')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, blank=True, null=True, verbose_name='Tipo')
    fabricante = models.CharField(max_length=100, blank=True, null=True, verbose_name='Fabricante')
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Modelo')
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de Série')
    data_instalacao = models.DateField(blank=True, null=True, verbose_name='Data de Instalação')
    status_operacional = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='operando', 
        verbose_name='Status Operacional'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    tenant_id = models.IntegerField(default=1, verbose_name='Tenant ID')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Data de Exclusão')
    prioridade = models.CharField(
        max_length=20, 
        choices=PRIORIDADE_CHOICES, 
        default='media', 
        verbose_name='Prioridade'
    )
    data_aquisicao = models.DateField(null=True, blank=True, verbose_name='Data de Aquisição')
    valor_aquisicao = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Valor de Aquisição'
    )
    garantia_ate = models.DateField(null=True, blank=True, verbose_name='Garantia até')
    responsavel = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Responsável',
        related_name='equipamentos_responsavel'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
        ordering = ['nome']
        
    def __str__(self):
        return f"{self.nome} ({self.codigo})"
    
    def get_absolute_url(self):
        return reverse('locations:equipamento_detail', kwargs={'pk': self.pk})
    
    def get_status_color(self):
        colors = {
            'operando': 'success',
            'manutencao': 'warning',
            'inativo': 'danger',
            'almoxarifado': 'info',
        }
        return colors.get(self.status_operacional, 'secondary')
    
    def get_priority_color(self):
        colors = {
            'baixa': 'success',
            'media': 'warning',
            'alta': 'danger',
            'critica': 'dark'
        }
        return colors.get(self.prioridade, 'secondary')
    
    def get_tipo_display_custom(self):
        return self.get_tipo_display() if self.tipo else 'Não informado'
    
    @property
    def is_garantia_valida(self):
        if self.garantia_ate:
            return self.garantia_ate >= date.today()
        return False
