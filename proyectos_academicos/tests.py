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



class DashboardViewTestCase(TestCase):
    """
    Tests para verificar las vistas de dashboard diferenciadas por rol.
    Requisitos: 1.5, 13.3, 13.4, 13.5
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Obtener o crear grupos
        self.grupo_estudiante, _ = Group.objects.get_or_create(name='estudiante')
        self.grupo_docente, _ = Group.objects.get_or_create(name='docente')
        
        # Crear usuarios
        self.estudiante = User.objects.create_user(
            username='estudiante_test',
            email='estudiante@test.com',
            password='testpass123',
            first_name='Juan',
            last_name='Estudiante'
        )
        self.estudiante.groups.add(self.grupo_estudiante)
        
        self.docente = User.objects.create_user(
            username='docente_test',
            email='docente@test.com',
            password='testpass123',
            first_name='María',
            last_name='Docente'
        )
        self.docente.groups.add(self.grupo_docente)
        
        self.usuario_sin_rol = User.objects.create_user(
            username='sin_rol',
            email='sinrol@test.com',
            password='testpass123'
        )
        
        # Crear proyectos de prueba
        pdf_content = b'%PDF-1.4 fake pdf content'
        
        # Proyecto del estudiante
        pdf_file1 = SimpleUploadedFile(
            'proyecto1.pdf',
            pdf_content,
            content_type='application/pdf'
        )
        self.proyecto_estudiante = Proyecto.objects.create(
            titulo='Proyecto del Estudiante',
            descripcion='Descripción del proyecto',
            estudiante=self.estudiante,
            documento=pdf_file1,
            estado='enviado'
        )
        
        # Proyecto de otro estudiante
        otro_estudiante = User.objects.create_user(
            username='otro_estudiante',
            email='otro@test.com',
            password='testpass123'
        )
        otro_estudiante.groups.add(self.grupo_estudiante)
        
        pdf_file2 = SimpleUploadedFile(
            'proyecto2.pdf',
            pdf_content,
            content_type='application/pdf'
        )
        self.proyecto_otro = Proyecto.objects.create(
            titulo='Proyecto de Otro Estudiante',
            descripcion='Otro proyecto',
            estudiante=otro_estudiante,
            documento=pdf_file2,
            estado='revision'
        )
    
    def test_dashboard_requiere_autenticacion(self):
        """
        Verificar que el dashboard requiere autenticación.
        Requisito: 1.5
        """
        response = self.client.get('/dashboard/')
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_dashboard_estudiante_muestra_solo_propios_proyectos(self):
        """
        Verificar que estudiantes solo ven sus propios proyectos.
        Requisitos: 13.3, 13.4
        """
        self.client.login(username='estudiante_test', password='testpass123')
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_role'], 'estudiante')
        
        # Verificar que solo ve su propio proyecto
        proyectos = response.context['proyectos']
        self.assertEqual(proyectos.count(), 1)
        self.assertEqual(proyectos.first().id, self.proyecto_estudiante.id)
        
        # Verificar que el template contiene el botón de crear proyecto
        self.assertContains(response, 'Crear Proyecto')
    
    def test_dashboard_docente_muestra_todos_proyectos(self):
        """
        Verificar que docentes ven todos los proyectos.
        Requisitos: 13.3, 13.5
        """
        self.client.login(username='docente_test', password='testpass123')
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_role'], 'docente')
        
        # Verificar que ve todos los proyectos
        proyectos = response.context['proyectos']
        self.assertEqual(proyectos.count(), 2)
        
        # Verificar que el template contiene enlace a estadísticas
        self.assertContains(response, 'Ver Estadísticas')
    
    def test_dashboard_usuario_sin_rol(self):
        """
        Verificar que usuarios sin rol ven mensaje apropiado.
        Requisito: 13.3
        """
        self.client.login(username='sin_rol', password='testpass123')
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_role'], 'sin_rol')
        self.assertEqual(response.context['total_proyectos'], 0)
        
        # Verificar mensaje de sin rol
        self.assertContains(response, 'Sin Rol Asignado')
        self.assertContains(response, 'contacta al administrador')
    
    def test_dashboard_muestra_badges_estado(self):
        """
        Verificar que el dashboard muestra badges de estado correctamente.
        Requisito: 13.4
        """
        self.client.login(username='docente_test', password='testpass123')
        response = self.client.get('/dashboard/')
        
        # Verificar que muestra badges de estado (enviado y revision)
        self.assertContains(response, 'Enviado')
        self.assertContains(response, 'En Revisión')
    
    def test_dashboard_responsive_design(self):
        """
        Verificar que el dashboard tiene diseño responsive.
        Requisito: 12.6
        """
        self.client.login(username='estudiante_test', password='testpass123')
        response = self.client.get('/dashboard/')
        
        # Verificar clases de Tailwind para responsive design
        self.assertContains(response, 'sm:flex-row')  # Responsive flex
        self.assertContains(response, 'md:block')     # Desktop table
        self.assertContains(response, 'md:hidden')    # Mobile cards
        self.assertContains(response, 'lg:grid-cols-3')  # Grid responsive
    
    def test_dashboard_muestra_total_proyectos(self):
        """
        Verificar que el dashboard muestra el total de proyectos.
        Requisito: 13.4, 13.5
        """
        self.client.login(username='estudiante_test', password='testpass123')
        response = self.client.get('/dashboard/')
        
        self.assertEqual(response.context['total_proyectos'], 1)
        self.assertContains(response, 'Total de Proyectos')
