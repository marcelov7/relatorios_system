from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta


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
        'authentication.User',
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
        'authentication.User',
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


class Motor(models.Model):
    """Modelo para gerenciamento de motores elétricos"""
    
    STATUS_OPERACIONAL_CHOICES = [
        ('operando', 'Operando'),
        ('manutencao', 'Manutenção'),
        ('inativo', 'Inativo'),
        ('almoxarifado', 'Almoxarifado'),
    ]
    
    TIPO_CHOICES = [
        ('monofasico', 'Monofásico'),
        ('trifasico', 'Trifásico'),
        ('cc', 'Corrente Contínua'),
        ('servo', 'Servo Motor'),
        ('passo', 'Motor de Passo'),
        ('outro', 'Outro'),
    ]
    
    # Identificação
    nome = models.CharField(max_length=100, verbose_name='Nome do Motor')
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name='Tipo')
    
    # Especificações Técnicas
    potencia = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Potência (CV)',
        help_text='Potência em cavalos-vapor (CV)'
    )
    voltagem = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Voltagem (V)',
        help_text='Tensão nominal em Volts'
    )
    corrente = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Corrente (A)',
        help_text='Corrente nominal em Ampères'
    )
    rpm = models.IntegerField(verbose_name='RPM', help_text='Rotações por minuto')
    
    # Informações do Fabricante
    fabricante = models.CharField(max_length=100, verbose_name='Fabricante')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    numero_serie = models.CharField(max_length=100, unique=True, verbose_name='Número de Série')
    
    # Datas
    data_instalacao = models.DateField(blank=True, null=True, verbose_name='Data de Instalação')
    
    # Status
    status_operacional = models.CharField(
        max_length=20, 
        choices=STATUS_OPERACIONAL_CHOICES, 
        default='operando', 
        verbose_name='Status Operacional'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    
    # Local onde está instalado (relacionamento com Local)
    local = models.ForeignKey(
        Local, 
        on_delete=models.CASCADE, 
        related_name='motores', 
        verbose_name='Local de Instalação'
    )
    
    # Responsável pelo motor
    responsavel = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Responsável',
        related_name='motores_responsavel'
    )
    
    # Timestamps
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    
    class Meta:
        verbose_name = 'Motor'
        verbose_name_plural = 'Motores'
        ordering = ['nome']
        
    def __str__(self):
        return f"{self.nome} ({self.codigo})"
    
    def get_absolute_url(self):
        return reverse('locations:motor_detail', kwargs={'pk': self.pk})
    
    def get_status_color(self):
        colors = {
            'operando': 'success',
            'manutencao': 'warning',
            'inativo': 'danger',
            'almoxarifado': 'info',
        }
        return colors.get(self.status_operacional, 'secondary')
    
    def get_potencia_kw(self):
        """Converte potência de CV para kW"""
        return round(float(self.potencia) * 0.735, 2)
    
    def get_status_display_icon(self):
        icons = {
            'operando': 'bi-play-circle-fill text-success',
            'manutencao': 'bi-tools text-warning', 
            'inativo': 'bi-stop-circle-fill text-danger',
            'almoxarifado': 'bi-archive-fill text-info',
        }
        return icons.get(self.status_operacional, 'bi-circle text-secondary')
    
    @property
    def eficiencia_estimada(self):
        """Calcula eficiência estimada baseada na potência"""
        potencia_num = float(self.potencia)
        if potencia_num <= 1:
            return 75  # 75% para motores pequenos
        elif potencia_num <= 10:
            return 85  # 85% para motores médios
        else:
            return 92  # 92% para motores grandes
