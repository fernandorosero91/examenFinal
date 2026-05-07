from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_pdf(file):
    """
    Validador personalizado que verifica que el archivo tenga extensión .pdf.
    Requisitos: 3.1, 3.2, 3.3
    """
    if not file.name.lower().endswith('.pdf'):
        raise ValidationError('Solo se permiten archivos PDF.')


class Proyecto(models.Model):
    """
    Modelo que representa un proyecto académico enviado por un estudiante.
    Requisitos: 17.1, 17.2, 17.4, 17.5
    """

    ESTADO_CHOICES = [
        ('enviado', 'Enviado'),
        ('revision', 'En Revisión'),
        ('aprobado', 'Aprobado'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proyectos'
    )
    documento = models.FileField(
        upload_to='proyectos/',
        validators=[validate_pdf]
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='enviado'
    )
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    calificacion = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )

    def clean(self):
        """
        Validación de calificación: debe estar entre 0.0 y 5.0.
        Requisitos: 4.5, 4.6
        """
        if self.calificacion is not None:
            if not (0.0 <= float(self.calificacion) <= 5.0):
                raise ValidationError(
                    'La calificación debe estar entre 0.0 y 5.0.'
                )

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-fecha_envio']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'


class Comentario(models.Model):
    """
    Modelo que representa un comentario asociado a un proyecto académico.
    Requisitos: 17.3, 17.4, 17.5
    """

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comentario de {self.usuario.username} en "{self.proyecto.titulo}"'

    class Meta:
        ordering = ['fecha']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
