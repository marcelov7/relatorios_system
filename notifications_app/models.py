from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationTemplate(models.Model):
    """Template para notificações"""
    NOTIFICATION_TYPES = [
        ('report_created', 'Relatório Criado'),
        ('report_completed', 'Relatório Concluído'),
        ('report_failed', 'Relatório Falhou'),
        ('user_registered', 'Usuário Registrado'),
        ('deadline_reminder', 'Lembrete de Prazo'),
        ('system_maintenance', 'Manutenção do Sistema'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nome')
    notification_type = models.CharField(
        max_length=50, 
        choices=NOTIFICATION_TYPES, 
        verbose_name='Tipo de Notificação'
    )
    title_template = models.CharField(max_length=200, verbose_name='Template do Título')
    message_template = models.TextField(verbose_name='Template da Mensagem')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Template de Notificação'
        verbose_name_plural = 'Templates de Notificações'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"


class UserNotificationSettings(models.Model):
    """Configurações de notificação do usuário"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Usuário',
        related_name='notification_settings'
    )
    
    # Tipos de notificação
    email_notifications = models.BooleanField(default=True, verbose_name='Notificações por Email')
    browser_notifications = models.BooleanField(default=True, verbose_name='Notificações do Navegador')
    
    # Notificações específicas
    report_created = models.BooleanField(default=True, verbose_name='Relatório Criado')
    report_completed = models.BooleanField(default=True, verbose_name='Relatório Concluído')
    report_failed = models.BooleanField(default=True, verbose_name='Relatório Falhou')
    deadline_reminders = models.BooleanField(default=True, verbose_name='Lembretes de Prazo')
    system_updates = models.BooleanField(default=False, verbose_name='Atualizações do Sistema')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Configuração de Notificação'
        verbose_name_plural = 'Configurações de Notificações'

    def __str__(self):
        return f"Configurações de {self.user.get_full_name()}"


class CustomNotification(models.Model):
    """Notificação personalizada"""
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Destinatário',
        related_name='custom_notifications'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Remetente',
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    
    title = models.CharField(max_length=200, verbose_name='Título')
    message = models.TextField(verbose_name='Mensagem')
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='normal',
        verbose_name='Prioridade'
    )
    
    # Status
    is_read = models.BooleanField(default=False, verbose_name='Lida')
    is_sent_by_email = models.BooleanField(default=False, verbose_name='Enviada por Email')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Lida em')

    class Meta:
        verbose_name = 'Notificação Personalizada'
        verbose_name_plural = 'Notificações Personalizadas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"

    def mark_as_read(self):
        """Marca a notificação como lida"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class NotificationLog(models.Model):
    """Log de notificações enviadas"""
    notification_type = models.CharField(max_length=50, verbose_name='Tipo')
    recipient_email = models.EmailField(verbose_name='Email do Destinatário')
    title = models.CharField(max_length=200, verbose_name='Título')
    message = models.TextField(verbose_name='Mensagem')
    
    # Status do envio
    is_sent = models.BooleanField(default=False, verbose_name='Enviada')
    error_message = models.TextField(blank=True, verbose_name='Mensagem de Erro')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Enviada em')

    class Meta:
        verbose_name = 'Log de Notificação'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.recipient_email}" 