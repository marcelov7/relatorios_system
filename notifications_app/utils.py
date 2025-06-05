from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from notifications.signals import notify
from .models import UserNotificationSettings, NotificationLog, CustomNotification
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def send_notification(user, title, message, notification_type='general', sender=None):
    """
    Enviar notificação para um usuário
    """
    try:
        # Verificar configurações do usuário
        settings_obj, created = UserNotificationSettings.objects.get_or_create(user=user)
        
        # Criar notificação no sistema
        notify.send(
            sender=sender or User.objects.filter(is_superuser=True).first(),
            recipient=user,
            verb=title,
            description=message,
        )
        
        # Enviar por email se habilitado
        if settings_obj.email_notifications:
            send_email_notification(user, title, message, notification_type)
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {str(e)}")
        return False


def send_email_notification(user, title, message, notification_type='general'):
    """
    Enviar notificação por email
    """
    try:
        # Criar contexto para o template
        context = {
            'user': user,
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'site_name': 'Sistema de Relatórios',
        }
        
        # Renderizar template de email
        html_message = render_to_string('notifications_app/email/notification.html', context)
        plain_message = render_to_string('notifications_app/email/notification.txt', context)
        
        # Enviar email
        success = send_mail(
            subject=f"[Sistema de Relatórios] {title}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Log do envio
        NotificationLog.objects.create(
            notification_type=notification_type,
            recipient_email=user.email,
            title=title,
            message=message,
            is_sent=success,
        )
        
        return success
        
    except Exception as e:
        logger.error(f"Erro ao enviar email: {str(e)}")
        
        # Log do erro
        NotificationLog.objects.create(
            notification_type=notification_type,
            recipient_email=user.email,
            title=title,
            message=message,
            is_sent=False,
            error_message=str(e),
        )
        
        return False


def send_bulk_notification(recipients, title, message, priority='normal', sender=None):
    """
    Enviar notificação para múltiplos usuários
    """
    results = []
    
    for user in recipients:
        # Criar notificação personalizada
        notification = CustomNotification.objects.create(
            recipient=user,
            sender=sender,
            title=title,
            message=message,
            priority=priority,
        )
        
        # Enviar notificação
        result = send_notification(user, title, message, 'bulk', sender)
        results.append({
            'user': user,
            'success': result,
            'notification_id': notification.id,
        })
    
    return results


def notify_report_created(report):
    """
    Notificar sobre criação de relatório
    """
    title = f"Novo relatório criado: {report.title}"
    message = f"O relatório '{report.title}' foi criado por {report.author.get_full_name()}."
    
    # Notificar gerentes
    managers = User.objects.filter(is_manager=True, is_active=True)
    for manager in managers:
        send_notification(manager, title, message, 'report_created', report.author)


def notify_report_completed(report):
    """
    Notificar sobre conclusão de relatório
    """
    title = f"Relatório concluído: {report.title}"
    message = f"O relatório '{report.title}' foi concluído com sucesso."
    
    # Notificar o autor
    send_notification(report.author, title, message, 'report_completed')
    
    # Notificar gerentes
    managers = User.objects.filter(is_manager=True, is_active=True)
    for manager in managers:
        if manager != report.author:
            send_notification(manager, title, message, 'report_completed', report.author)


def notify_report_failed(report, error_message=None):
    """
    Notificar sobre falha no relatório
    """
    title = f"Erro no relatório: {report.title}"
    message = f"O relatório '{report.title}' falhou durante o processamento."
    if error_message:
        message += f"\n\nErro: {error_message}"
    
    # Notificar o autor
    send_notification(report.author, title, message, 'report_failed')


def notify_deadline_reminder(user, reports_due):
    """
    Notificar sobre prazos próximos
    """
    if not reports_due:
        return
    
    title = f"Lembrete: {len(reports_due)} relatório(s) com prazo próximo"
    
    report_list = "\n".join([f"- {report.title}" for report in reports_due])
    message = f"Os seguintes relatórios têm prazos próximos:\n\n{report_list}"
    
    send_notification(user, title, message, 'deadline_reminder')


def get_user_notification_preferences(user):
    """
    Obter preferências de notificação do usuário
    """
    settings_obj, created = UserNotificationSettings.objects.get_or_create(user=user)
    return settings_obj


def create_system_notification(title, message, priority='normal'):
    """
    Criar notificação do sistema para todos os usuários
    """
    active_users = User.objects.filter(is_active=True)
    
    results = []
    for user in active_users:
        notification = CustomNotification.objects.create(
            recipient=user,
            title=title,
            message=message,
            priority=priority,
        )
        
        result = send_notification(user, title, message, 'system_notification')
        results.append({
            'user': user,
            'success': result,
            'notification_id': notification.id,
        })
    
    return results 