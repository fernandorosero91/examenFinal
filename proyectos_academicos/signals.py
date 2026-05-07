import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Comentario

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comentario)
def enviar_notificacion_comentario(sender, instance, created, **kwargs):
    """
    Signal handler que envía notificación por email cuando se crea un comentario.
    Requisitos: 6.1, 6.2, 6.3
    """
    if created:
        try:
            # Obtener información del comentario
            proyecto_titulo = instance.proyecto.titulo
            comentario_texto = instance.texto
            usuario_nombre = instance.usuario.get_full_name() or instance.usuario.username
            fecha = instance.fecha.strftime('%d/%m/%Y %H:%M')
            estudiante_email = instance.proyecto.estudiante.email
            
            # Construir el mensaje
            subject = f'Nuevo comentario en tu proyecto: {proyecto_titulo}'
            message = f"""
Hola {instance.proyecto.estudiante.get_full_name() or instance.proyecto.estudiante.username},

Has recibido un nuevo comentario en tu proyecto "{proyecto_titulo}".

Comentario de: {usuario_nombre}
Fecha: {fecha}

Mensaje:
{comentario_texto}

---
Sistema de Gestión de Proyectos Académicos
            """.strip()
            
            # Enviar email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[estudiante_email],
                fail_silently=False
            )
            
            logger.info(f'Email enviado a {estudiante_email} por comentario en proyecto {proyecto_titulo}')
            
        except Exception as e:
            # Registrar el error pero no interrumpir la creación del comentario
            logger.error(f'Error al enviar email de notificación: {str(e)}')
