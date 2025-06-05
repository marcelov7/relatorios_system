from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from notifications.models import Notification
from .models import CustomNotification, UserNotificationSettings
from .forms import CustomNotificationForm, NotificationSettingsForm
from .utils import send_notification


@login_required
def notification_list(request):
    """Lista de notificações do usuário"""
    # Notificações do django-notifications-hq
    django_notifications = request.user.notifications.all()
    
    # Notificações personalizadas
    custom_notifications = CustomNotification.objects.filter(recipient=request.user)
    
    # Combinar e paginar
    all_notifications = []
    
    # Adicionar notificações do django-notifications-hq
    for notif in django_notifications:
        all_notifications.append({
            'type': 'django',
            'id': notif.id,
            'title': str(notif.verb),
            'message': str(notif.description) if notif.description else '',
            'is_read': notif.unread,
            'created_at': notif.timestamp,
            'priority': 'normal',
        })
    
    # Adicionar notificações personalizadas
    for notif in custom_notifications:
        all_notifications.append({
            'type': 'custom',
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'is_read': notif.is_read,
            'created_at': notif.created_at,
            'priority': notif.priority,
        })
    
    # Ordenar por data
    all_notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Paginação
    paginator = Paginator(all_notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    unread_count = request.user.notifications.unread().count() + \
                   CustomNotification.objects.filter(recipient=request.user, is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
    }
    
    return render(request, 'notifications_app/notification_list.html', context)


@login_required
def mark_as_read(request, notification_type, notification_id):
    """Marcar notificação como lida"""
    if notification_type == 'django':
        try:
            notification = get_object_or_404(
                Notification, 
                id=notification_id, 
                recipient=request.user
            )
            notification.mark_as_read()
        except:
            pass
    elif notification_type == 'custom':
        try:
            notification = get_object_or_404(
                CustomNotification, 
                id=notification_id, 
                recipient=request.user
            )
            notification.mark_as_read()
        except:
            pass
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications_app:list')


@login_required
def mark_all_as_read(request):
    """Marcar todas as notificações como lidas"""
    if request.method == 'POST':
        # Marcar notificações do django-notifications-hq
        request.user.notifications.mark_all_as_read()
        
        # Marcar notificações personalizadas
        CustomNotification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).update(is_read=True)
        
        messages.success(request, 'Todas as notificações foram marcadas como lidas.')
    
    return redirect('notifications_app:list')


@login_required
def delete_notification(request, notification_type, notification_id):
    """Excluir notificação"""
    if request.method == 'POST':
        if notification_type == 'django':
            try:
                notification = get_object_or_404(
                    Notification, 
                    id=notification_id, 
                    recipient=request.user
                )
                notification.delete()
            except:
                pass
        elif notification_type == 'custom':
            try:
                notification = get_object_or_404(
                    CustomNotification, 
                    id=notification_id, 
                    recipient=request.user
                )
                notification.delete()
            except:
                pass
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('notifications_app:list')


@login_required
def send_custom_notification(request):
    """Enviar notificação personalizada"""
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para enviar notificações.')
        return redirect('notifications_app:list')
    
    if request.method == 'POST':
        form = CustomNotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.sender = request.user
            notification.save()
            
            # Enviar por email se configurado
            send_notification(
                notification.recipient,
                notification.title,
                notification.message,
                notification_type='custom'
            )
            
            messages.success(request, 'Notificação enviada com sucesso!')
            return redirect('notifications_app:list')
    else:
        form = CustomNotificationForm()
    
    return render(request, 'notifications_app/send_notification.html', {'form': form})


@login_required
def notification_settings(request):
    """Configurações de notificação do usuário"""
    settings, created = UserNotificationSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('notifications_app:settings')
    else:
        form = NotificationSettingsForm(instance=settings)
    
    return render(request, 'notifications_app/settings.html', {'form': form})


@login_required
def api_unread_count(request):
    """API para contar notificações não lidas"""
    django_unread = request.user.notifications.unread().count()
    custom_unread = CustomNotification.objects.filter(
        recipient=request.user, 
        is_read=False
    ).count()
    
    total_unread = django_unread + custom_unread
    
    return JsonResponse({
        'unread_count': total_unread,
        'django_unread': django_unread,
        'custom_unread': custom_unread,
    })


@login_required
def api_recent_notifications(request):
    """API para notificações recentes"""
    limit = int(request.GET.get('limit', 5))
    
    # Notificações do django-notifications-hq
    django_notifications = request.user.notifications.all()[:limit]
    
    # Notificações personalizadas
    custom_notifications = CustomNotification.objects.filter(
        recipient=request.user
    )[:limit]
    
    notifications = []
    
    # Adicionar notificações do django-notifications-hq
    for notif in django_notifications:
        notifications.append({
            'type': 'django',
            'id': notif.id,
            'title': str(notif.verb),
            'message': str(notif.description) if notif.description else '',
            'is_read': not notif.unread,
            'created_at': notif.timestamp.strftime('%d/%m/%Y %H:%M'),
            'priority': 'normal',
        })
    
    # Adicionar notificações personalizadas
    for notif in custom_notifications:
        notifications.append({
            'type': 'custom',
            'id': notif.id,
            'title': notif.title,
            'message': notif.message[:100] + '...' if len(notif.message) > 100 else notif.message,
            'is_read': notif.is_read,
            'created_at': notif.created_at.strftime('%d/%m/%Y %H:%M'),
            'priority': notif.priority,
        })
    
    # Ordenar por data
    notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    return JsonResponse({
        'notifications': notifications[:limit]
    }) 