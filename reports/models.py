from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid

User = get_user_model()


class ReportCategory(models.Model):
    """Categoria de relatórios"""
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


class Report(models.Model):
    """Modelo principal de relatórios"""
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descrição')
    category = models.ForeignKey(ReportCategory, on_delete=models.CASCADE, verbose_name='Categoria')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Status')
    
    # Datas
    start_date = models.DateField(verbose_name='Data Inicial')
    end_date = models.DateField(verbose_name='Data Final')
    
    # Arquivos
    pdf_file = models.FileField(upload_to='reports/pdf/', blank=True, null=True, verbose_name='Arquivo PDF')
    excel_file = models.FileField(upload_to='reports/excel/', blank=True, null=True, verbose_name='Arquivo Excel')
    
    # Metadados
    is_public = models.BooleanField(default=False, verbose_name='Público')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Visualizações')
    downloads_count = models.PositiveIntegerField(default=0, verbose_name='Downloads')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reports:detail', kwargs={'pk': self.pk})


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
        return f"{self.report.title} - {self.get_frequency_display()}" 