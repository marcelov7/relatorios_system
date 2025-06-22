from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

# Importar os modelos de locations
try:
    from locations.models import Local, Equipamento
except ImportError:
    # Em caso de problemas de importação circular
    Local = None
    Equipamento = None


class Report(models.Model):
    """Modelo de relatórios baseado na estrutura de banco desejada"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('resolvido', 'Resolvido'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    # Campos baseados na estrutura mostrada
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor', db_column='usuario_id', related_name='reports')
    atribuido_para = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Atribuído Para',
        related_name='reports_atribuidos',
        help_text='Usuário responsável por executar este relatório'
    )
    local = models.ForeignKey('locations.Local', on_delete=models.CASCADE, verbose_name='Local', related_name='reports', null=True, blank=True)
    equipamento = models.ForeignKey('locations.Equipamento', on_delete=models.CASCADE, verbose_name='Equipamento', related_name='reports', null=True, blank=True)
    data_ocorrencia = models.DateTimeField(verbose_name='Data da Ocorrência')
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(verbose_name='Descrição')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pendente', 
        verbose_name='Status'
    )
    prioridade = models.CharField(
        max_length=20, 
        choices=PRIORIDADE_CHOICES, 
        default='media', 
        verbose_name='Prioridade'
    )
    progresso = models.IntegerField(default=0, verbose_name='Progresso (%)')
    editavel = models.BooleanField(default=True, verbose_name='Editável')
    # Campo para upload de imagem principal
    imagem_principal = models.ImageField(
        upload_to='reports/images/', 
        null=True, 
        blank=True, 
        verbose_name='Imagem Principal'
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    tenant_id = models.IntegerField(default=1, verbose_name='Tenant ID')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deletado em')

    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-data_criacao']
        db_table = 'reports_report'

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('reports:detail', kwargs={'pk': self.pk})

    @property
    def author(self):
        """Propriedade para compatibilidade com código existente"""
        return self.usuario

    def is_completed(self):
        """Verifica se o relatório está concluído"""
        return self.status == 'resolvido'

    def get_progress_color(self):
        """Retorna cor baseada no progresso"""
        if self.progresso < 25:
            return 'danger'
        elif self.progresso < 50:
            return 'warning'
        elif self.progresso < 75:
            return 'info'
        else:
            return 'success'

    def get_priority_color(self):
        """Retorna cor baseada na prioridade"""
        colors = {
            'baixa': 'success',
            'media': 'warning',
            'alta': 'danger',
            'critica': 'dark'
        }
        return colors.get(self.prioridade, 'secondary')
    
    def pode_editar(self, user):
        """Verifica se o usuário pode editar o relatório"""
        return user == self.usuario or user.is_staff
    
    def pode_atualizar_status(self, user):
        """Verifica se o usuário pode atualizar o status/progresso"""
        # Autor sempre pode
        if user == self.usuario:
            return True
        # Usuário atribuído pode se o status não for resolvido
        if user == self.atribuido_para and self.status != 'resolvido':
            return True
        # Staff sempre pode
        if user.is_staff:
            return True
        return False
    
    def get_responsavel_atual(self):
        """Retorna o usuário responsável atual (atribuído ou autor)"""
        return self.atribuido_para or self.usuario
    
    def get_ultima_atualizacao(self):
        """Retorna a última atualização do relatório"""
        return self.atualizacoes.first()
    
    def get_total_atualizacoes(self):
        """Retorna o total de atualizações"""
        return self.atualizacoes.count()


class ReportImage(models.Model):
    """Modelo para múltiplas imagens anexadas ao relatório"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='imagens', verbose_name='Relatório')
    imagem = models.ImageField(upload_to='reports/anexos/', verbose_name='Imagem')
    descricao = models.CharField(max_length=200, blank=True, verbose_name='Descrição da Imagem')
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name='Data do Upload')
    ordem = models.PositiveIntegerField(default=0, verbose_name='Ordem de Exibição')

    class Meta:
        verbose_name = 'Imagem do Relatório'
        verbose_name_plural = 'Imagens dos Relatórios'
        ordering = ['ordem', 'data_upload']

    def __str__(self):
        return f"{self.report.titulo} - Imagem {self.id}"


# Modelo simplificado para categorias (opcional)
class ReportCategory(models.Model):
    """Categoria de relatórios - modelo simplificado"""
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Cor')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Categoria de Relatório'
        verbose_name_plural = 'Categorias de Relatórios'
        ordering = ['name']

    def __str__(self):
        return self.name


class ReportData(models.Model):
    """Dados dos relatórios"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='data', verbose_name='Relatório')
    field_name = models.CharField(max_length=100, verbose_name='Nome do Campo')
    field_value = models.TextField(verbose_name='Valor do Campo')
    data_type = models.CharField(max_length=20, choices=[
        ('text', 'Texto'),
        ('number', 'Número'),
        ('date', 'Data'),
        ('boolean', 'Booleano'),
    ], default='text', verbose_name='Tipo de Dado')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Dado do Relatório'
        verbose_name_plural = 'Dados dos Relatórios'
        unique_together = ['report', 'field_name']

    def __str__(self):
        return f"{self.report.title} - {self.field_name}"


class ReportSchedule(models.Model):
    """Agendamento de relatórios"""
    FREQUENCY_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]

    report = models.OneToOneField(Report, on_delete=models.CASCADE, verbose_name='Relatório')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name='Frequência')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    next_run = models.DateTimeField(verbose_name='Próxima Execução')
    last_run = models.DateTimeField(blank=True, null=True, verbose_name='Última Execução')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Agendamento de Relatório'
        verbose_name_plural = 'Agendamentos de Relatórios'

    def __str__(self):
        return f"{self.report.titulo} - {self.get_frequency_display()}"


class ReportUpdate(models.Model):
    """Histórico de atualizações do relatório"""
    
    report = models.ForeignKey(
        Report, 
        on_delete=models.CASCADE, 
        related_name='atualizacoes', 
        verbose_name='Relatório'
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Usuário que Atualizou'
    )
    progresso_anterior = models.IntegerField(verbose_name='Progresso Anterior (%)')
    progresso_novo = models.IntegerField(verbose_name='Novo Progresso (%)')
    status_anterior = models.CharField(max_length=20, verbose_name='Status Anterior')
    status_novo = models.CharField(max_length=20, verbose_name='Novo Status')
    descricao_atualizacao = models.TextField(verbose_name='Descrição da Atualização')
    data_atualizacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Atualização')
    
    class Meta:
        verbose_name = 'Atualização de Relatório'
        verbose_name_plural = 'Atualizações de Relatórios'
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        return f"{self.report.titulo} - {self.progresso_anterior}% → {self.progresso_novo}%"
    
    def get_progresso_diferenca(self):
        """Retorna a diferença de progresso"""
        return self.progresso_novo - self.progresso_anterior
    
    def get_status_color(self):
        """Retorna cor baseada no novo status"""
        colors = {
            'pendente': 'secondary',
            'em_andamento': 'warning',
            'resolvido': 'success'
        }
        return colors.get(self.status_novo, 'secondary')


class ReportUpdateImage(models.Model):
    """Imagens anexadas às atualizações do relatório"""
    
    update = models.ForeignKey(
        ReportUpdate, 
        on_delete=models.CASCADE, 
        related_name='imagens', 
        verbose_name='Atualização'
    )
    imagem = models.ImageField(
        upload_to='reports/updates/', 
        verbose_name='Imagem da Atualização'
    )
    descricao = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Descrição da Imagem'
    )
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name='Data do Upload')
    
    class Meta:
        verbose_name = 'Imagem da Atualização'
        verbose_name_plural = 'Imagens das Atualizações'
        ordering = ['data_upload']
    
    def __str__(self):
        return f"Imagem - {self.update.report.titulo}" 