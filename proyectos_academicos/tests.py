from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core import mail
from .models import Proyecto, Comentario
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile


class EmailNotificationTestCase(TestCase):
    """
    Tests para verificar el sistema de notificaciones por email.
    Requisitos: 6.1, 6.2, 6.3
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Obtener o crear grupos
        self.grupo_estudiante, _ = Group.objects.get_or_create(name='estudiante')
        self.grupo_docente, _ = Group.objects.get_or_create(name='docente')
        
        # Crear usuarios
        self.estudiante = User.objects.create_user(
            username='estudiante1',
            email='estudiante1@test.com',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.estudiante.groups.add(self.grupo_estudiante)
        
        self.docente = User.objects.create_user(
            username='docente1',
            email='docente1@test.com',
            password='testpass123',
            first_name='María',
            last_name='García'
        )
        self.docente.groups.add(self.grupo_docente)
        
        # Crear un archivo PDF de prueba
        pdf_content = b'%PDF-1.4 fake pdf content'
        pdf_file = SimpleUploadedFile(
            'test_proyecto.pdf',
            pdf_content,
            content_type='application/pdf'
        )
        
        # Crear proyecto
        self.proyecto = Proyecto.objects.create(
            titulo='Proyecto de Prueba',
            descripcion='Descripción del proyecto de prueba',
            estudiante=self.estudiante,
            documento=pdf_file,
            estado='enviado'
        )
    
    def test_email_enviado_al_crear_comentario(self):
        """
        Verificar que se envía un email cuando se crea un comentario.
        Requisitos: 6.1, 6.2
        """
        # Limpiar el outbox de emails
        mail.outbox = []
        
        # Crear un comentario
        comentario = Comentario.objects.create(
            proyecto=self.proyecto,
            usuario=self.docente,
            texto='Este es un comentario de prueba'
        )
        
        # Verificar que se envió un email
        self.assertEqual(len(mail.outbox), 1)
        
        # Verificar el contenido del email
        email = mail.outbox[0]
        self.assertIn(self.proyecto.titulo, email.subject)
        self.assertIn(self.estudiante.email, email.to)
        self.assertIn(self.proyecto.titulo, email.body)
        self.assertIn(comentario.texto, email.body)
        self.assertIn(self.docente.get_full_name(), email.body)
    
    def test_email_no_interrumpe_creacion_comentario(self):
        """
        Verificar que si falla el envío de email, el comentario se crea igual.
        Requisitos: 6.3
        """
        # Crear comentario (aunque el email falle, el comentario debe crearse)
        comentario = Comentario.objects.create(
            proyecto=self.proyecto,
            usuario=self.docente,
            texto='Comentario que debe crearse aunque falle el email'
        )
        
        # Verificar que el comentario se creó
        self.assertIsNotNone(comentario.id)
        self.assertEqual(comentario.texto, 'Comentario que debe crearse aunque falle el email')
        self.assertEqual(Comentario.objects.count(), 1)
    
    def test_email_incluye_informacion_requerida(self):
        """
        Verificar que el email incluye toda la información requerida.
        Requisitos: 6.2
        """
        mail.outbox = []
        
        comentario = Comentario.objects.create(
            proyecto=self.proyecto,
            usuario=self.docente,
            texto='Comentario con información completa'
        )
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Verificar que incluye: título del proyecto, texto del comentario,
        # nombre del usuario que comenta, y fecha
        self.assertIn(self.proyecto.titulo, email.body)
        self.assertIn(comentario.texto, email.body)
        self.assertIn(self.docente.get_full_name(), email.body)
        # La fecha está en el body (formato dd/mm/yyyy)
        self.assertRegex(email.body, r'\d{2}/\d{2}/\d{4}')

