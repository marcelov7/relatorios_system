# Generated migration for notifications_app

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
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nome')),
                ('subject', models.CharField(max_length=200, verbose_name='Assunto')),
                ('message', models.TextField(verbose_name='Mensagem')),
                ('template_type', models.CharField(choices=[('email', 'E-mail'), ('system', 'Sistema'), ('sms', 'SMS')], default='system', max_length=20, verbose_name='Tipo')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Template de Notificação',
                'verbose_name_plural': 'Templates de Notificações',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('message', models.TextField(verbose_name='Mensagem')),
                ('notification_type', models.CharField(choices=[('info', 'Informação'), ('success', 'Sucesso'), ('warning', 'Aviso'), ('error', 'Erro')], default='info', max_length=20, verbose_name='Tipo')),
                ('is_read', models.BooleanField(default=False, verbose_name='Lida')),
                ('is_sent', models.BooleanField(default=False, verbose_name='Enviada')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='Enviada em')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='Lida em')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criada em')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Destinatário')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_notifications', to=settings.AUTH_USER_MODEL, verbose_name='Remetente')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notifications_app.notificationtemplate', verbose_name='Template')),
            ],
            options={
                'verbose_name': 'Notificação',
                'verbose_name_plural': 'Notificações',
                'ordering': ['-created_at'],
            },
        ),
    ] 