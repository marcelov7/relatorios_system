# Generated migration for reports app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('color', models.CharField(default='#007bff', max_length=7, verbose_name='Cor')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativa')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Categoria de Relatório',
                'verbose_name_plural': 'Categorias de Relatórios',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(verbose_name='Descrição')),
                ('content', models.TextField(verbose_name='Conteúdo')),
                ('status', models.CharField(choices=[('draft', 'Rascunho'), ('pending', 'Pendente'), ('approved', 'Aprovado'), ('rejected', 'Rejeitado')], default='draft', max_length=20, verbose_name='Status')),
                ('priority', models.CharField(choices=[('low', 'Baixa'), ('medium', 'Média'), ('high', 'Alta'), ('urgent', 'Urgente')], default='medium', max_length=20, verbose_name='Prioridade')),
                ('is_public', models.BooleanField(default=False, verbose_name='Público')),
                ('file_attachment', models.FileField(blank=True, null=True, upload_to='reports/attachments/', verbose_name='Anexo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_reports', to=settings.AUTH_USER_MODEL, verbose_name='Aprovado por')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='reports.reportcategory', verbose_name='Categoria')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_reports', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Relatório',
                'verbose_name_plural': 'Relatórios',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReportData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=100, verbose_name='Nome do Campo')),
                ('field_value', models.TextField(verbose_name='Valor do Campo')),
                ('field_type', models.CharField(choices=[('text', 'Texto'), ('number', 'Número'), ('date', 'Data'), ('boolean', 'Booleano'), ('json', 'JSON')], default='text', max_length=20, verbose_name='Tipo do Campo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_fields', to='reports.report', verbose_name='Relatório')),
            ],
            options={
                'verbose_name': 'Dados do Relatório',
                'verbose_name_plural': 'Dados dos Relatórios',
                'ordering': ['field_name'],
            },
        ),
    ] 