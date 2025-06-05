from django import forms
from django.contrib.auth import get_user_model
from .models import CustomNotification, UserNotificationSettings

User = get_user_model()


class CustomNotificationForm(forms.ModelForm):
    """Formulário para enviar notificações personalizadas"""
    
    class Meta:
        model = CustomNotification
        fields = ['recipient', 'title', 'message', 'priority']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título da notificação'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mensagem da notificação'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'].queryset = User.objects.filter(is_active=True)


class NotificationSettingsForm(forms.ModelForm):
    """Formulário para configurações de notificação"""
    
    class Meta:
        model = UserNotificationSettings
        fields = [
            'email_notifications', 'browser_notifications',
            'report_created', 'report_completed', 'report_failed',
            'deadline_reminders', 'system_updates'
        ]
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'browser_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'report_created': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'report_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'report_failed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'deadline_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'system_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BulkNotificationForm(forms.Form):
    """Formulário para envio em massa de notificações"""
    
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        label='Destinatários'
    )
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título da notificação'
        }),
        label='Título'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Mensagem da notificação'
        }),
        label='Mensagem'
    )
    
    priority = forms.ChoiceField(
        choices=CustomNotification.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='normal',
        label='Prioridade'
    )
    
    send_email = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Enviar por email também'
    ) 