from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modelo de usuário extendido"""
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    departamento = models.CharField(max_length=100, blank=True, verbose_name='Departamento')
    cargo = models.CharField(max_length=100, blank=True, verbose_name='Cargo')
    foto_perfil = models.ImageField(upload_to='perfil/', blank=True, null=True, verbose_name='Foto do Perfil')
    is_manager = models.BooleanField(default=False, verbose_name='É Gerente?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.username

    def get_full_name(self):
        """Retorna o nome completo do usuário"""
        return f"{self.first_name} {self.last_name}".strip() or self.username 