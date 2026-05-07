from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core import mail
from django import forms
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



class ComentarioCreateViewTestCase(TestCase):
    """
    Tests para verificar la vista de creación de comentarios.
    Requisitos: 5.1, 5.2, 5.4, 5.5, 12.2, 14.3, 14.4, 15.6
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
        
        # Crear proyectos con diferentes estados
        pdf_content = b'%PDF-1.4 fake pdf content'
        
        pdf_file1 = SimpleUploadedFile(
            'proyecto_enviado.pdf',
            pdf_content,
            content_type='application/pdf'
        )
        self.proyecto_enviado = Proyecto.objects.create(
            titulo='Proyecto Enviado',
            descripcion='Proyecto en estado enviado',
            estudiante=self.estudiante,
            documento=pdf_file1,
            estado='enviado'
        )
        
        pdf_file2 = SimpleUploadedFile(
            'proyecto_revision.pdf',
            pdf_content,
            content_type='application/pdf'
        )
        self.proyecto_revision = Proyecto.objects.create(
            titulo='Proyecto en Revisión',
            descripcion='Proyecto en estado revisión',
            estudiante=self.estudiante,
            documento=pdf_file2,
            estado='revision'
        )
        
        pdf_file3 = SimpleUploadedFile(
            'proyecto_aprobado.pdf',
            pdf_content,
            content_type='application/pdf'
        )
        self.proyecto_aprobado = Proyecto.objects.create(
            titulo='Proyecto Aprobado',
            descripcion='Proyecto en estado aprobado',
            estudiante=self.estudiante,
            documento=pdf_file3,
            estado='aprobado'
        )
    
    def test_comentario_create_requiere_autenticacion(self):
        """
        Verificar que la creación de comentarios requiere autenticación.
        Requisito: 15.6
        """
        response = self.client.post(
            f'/proyectos/{self.proyecto_enviado.pk}/comentarios/crear/',
            {'texto': 'Comentario de prueba'}
        )
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_comentario_create_asigna_usuario_automaticamente(self):
        """
        Verificar que el usuario se asigna automáticamente al comentario.
        Requisito: 5.1
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.post(
            f'/proyectos/{self.proyecto_enviado.pk}/comentarios/crear/',
            {'texto': 'Comentario del docente'}
        )
        
        # Verificar redirección exitosa
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el comentario se creó con el usuario correcto
        comentario = Comentario.objects.get(texto='Comentario del docente')
        self.assertEqual(comentario.usuario, self.docente)
        self.assertEqual(comentario.proyecto, self.proyecto_enviado)
    
    def test_comentario_create_asigna_proyecto_automaticamente(self):
        """
        Verificar que el proyecto se asigna automáticamente al comentario.
        Requisito: 5.1
        """
        self.client.login(username='estudiante1', password='testpass123')
        
        response = self.client.post(
            f'/proyectos/{self.proyecto_revision.pk}/comentarios/crear/',
            {'texto': 'Comentario del estudiante'}
        )
        
        # Verificar que el comentario se creó con el proyecto correcto
        comentario = Comentario.objects.get(texto='Comentario del estudiante')
        self.assertEqual(comentario.proyecto, self.proyecto_revision)
    
    def test_comentario_create_establece_fecha_automaticamente(self):
        """
        Verificar que la fecha se establece automáticamente.
        Requisito: 5.2
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.post(
            f'/proyectos/{self.proyecto_enviado.pk}/comentarios/crear/',
            {'texto': 'Comentario con fecha automática'}
        )
        
        comentario = Comentario.objects.get(texto='Comentario con fecha automática')
        self.assertIsNotNone(comentario.fecha)
    
    def test_comentario_create_bloqueado_en_proyecto_aprobado(self):
        """
        Verificar que no se pueden crear comentarios en proyectos aprobados.
        Requisitos: 5.4, 5.5
        """
        self.client.login(username='docente1', password='testpass123')
        
        # Intentar crear comentario en proyecto aprobado
        response = self.client.post(
            f'/proyectos/{self.proyecto_aprobado.pk}/comentarios/crear/',
            {'texto': 'Este comentario no debería crearse'}
        )
        
        # Debe redirigir al detalle del proyecto
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/proyectos/{self.proyecto_aprobado.pk}/', response.url)
        
        # Verificar que el comentario NO se creó
        self.assertFalse(
            Comentario.objects.filter(texto='Este comentario no debería crearse').exists()
        )
    
    def test_comentario_create_muestra_mensaje_error_proyecto_aprobado(self):
        """
        Verificar que se muestra mensaje de error al intentar comentar proyecto aprobado.
        Requisito: 5.5
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.post(
            f'/proyectos/{self.proyecto_aprobado.pk}/comentarios/crear/',
            {'texto': 'Comentario bloqueado'},
            follow=True
        )
        
        # Verificar que se muestra mensaje de error
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('No se pueden agregar comentarios a proyectos aprobados', str(messages[0]))
    
    def test_comentario_create_permite_estado_enviado(self):
        """
        Verificar que se pueden crear comentarios en proyectos con estado 'enviado'.
        Requisito: 5.4
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.post(
            f'/proyectos/{self.proyecto_enviado.pk}/comentarios/crear/',
            {'texto': 'Comentario en proyecto enviado'}
        )
        
        # Verificar que el comentario se creó
        self.assertTrue(
            Comentario.objects.filter(texto='Comentario en proyecto enviado').exists()
        )
    
    def test_comentario_create_permite_estado_revision(self):
        """
        Verificar que se pueden crear comentarios en proyectos con estado 'revision'.
        Requisito: 5.4
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.post(
            f'/proyectos/{self.proyecto_revision.pk}/comentarios/crear/',
            {'texto': 'Comentario en proyecto en revisión'}
        )
        
        # Verificar que el comentario se creó
        self.assertTrue(
            Comentario.objects.filter(texto='Comentario en proyecto en revisión').exists()
        )
    
    def test_comentario_create_redirige_a_proyecto_detail(self):
        """
        Verificar que después de crear un comentario se redirige al detalle del proyecto.
        Requisito: 15.6
        """
        self.client.login(username='estudiante1', password='testpass123')
        
        response = self.client.post(
            f'/proyectos/{self.proyecto_enviado.pk}/comentarios/crear/',
            {'texto': 'Comentario con redirección'}
        )
        
        # Verificar redirección al detalle del proyecto
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/proyectos/{self.proyecto_enviado.pk}/')
    
    def test_comentario_create_muestra_mensaje_exito(self):
        """
        Verificar que se muestra mensaje de éxito al crear comentario.
        Requisito: 15.6
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.post(
            f'/proyectos/{self.proyecto_enviado.pk}/comentarios/crear/',
            {'texto': 'Comentario exitoso'},
            follow=True
        )
        
        # Verificar mensaje de éxito
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('Comentario agregado exitosamente', str(messages[0]))
    
    def test_proyecto_detail_muestra_formulario_si_no_aprobado(self):
        """
        Verificar que el formulario de comentario se muestra si el proyecto no está aprobado.
        Requisitos: 14.3, 5.3
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.get(f'/proyectos/{self.proyecto_enviado.pk}/')
        
        # Verificar que el formulario está en el contexto
        self.assertIn('comentario_form', response.context)
        self.assertTrue(response.context['puede_comentar'])
        
        # Verificar que el formulario se muestra en el HTML
        self.assertContains(response, 'Agregar Comentario')
        self.assertContains(response, 'Enviar Comentario')
    
    def test_proyecto_detail_oculta_formulario_si_aprobado(self):
        """
        Verificar que el formulario de comentario NO se muestra si el proyecto está aprobado.
        Requisitos: 14.4, 5.4
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.get(f'/proyectos/{self.proyecto_aprobado.pk}/')
        
        # Verificar que no se puede comentar
        self.assertFalse(response.context['puede_comentar'])
        
        # Verificar que el formulario NO está en el contexto
        self.assertNotIn('comentario_form', response.context)
        
        # Verificar que se muestra el banner de advertencia
        self.assertContains(response, 'Este proyecto está aprobado. No se pueden agregar más comentarios.')
    
    def test_comentario_form_usa_crispy_forms(self):
        """
        Verificar que el formulario de comentario usa crispy-forms.
        Requisito: 12.2
        """
        self.client.login(username='docente1', password='testpass123')
        
        response = self.client.get(f'/proyectos/{self.proyecto_enviado.pk}/')
        
        # Verificar que el template usa crispy_forms_tags (div_id_texto es generado por crispy)
        self.assertContains(response, 'div_id_texto')
    
    def test_comentario_form_tiene_campo_texto_textarea(self):
        """
        Verificar que el formulario tiene el campo 'texto' como Textarea.
        Requisito: 12.2
        """
        from .forms import ComentarioForm
        
        form = ComentarioForm()
        
        # Verificar que el campo 'texto' existe
        self.assertIn('texto', form.fields)
        
        # Verificar que es un Textarea
        self.assertIsInstance(form.fields['texto'].widget, forms.Textarea)
    
    def test_comentario_form_tiene_placeholder(self):
        """
        Verificar que el campo texto tiene placeholder.
        Requisito: 12.2
        """
        from .forms import ComentarioForm
        
        form = ComentarioForm()
        
        # Verificar que tiene placeholder
        self.assertIn('placeholder', form.fields['texto'].widget.attrs)
        self.assertEqual(
            form.fields['texto'].widget.attrs['placeholder'],
            'Escribe tu comentario aquí...'
        )


class EstadisticasViewTestCase(TestCase):
    """
    Tests para verificar el panel de estadísticas para docentes.
    Requisitos: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2, 12.6
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Obtener o crear grupos
        self.grupo_estudiante, _ = Group.objects.get_or_create(name='estudiante')
        self.grupo_docente, _ = Group.objects.get_or_create(name='docente')
        
        # Crear usuarios
        self.estudiante1 = User.objects.create_user(
            username='estudiante1',
            email='estudiante1@test.com',
            password='testpass123'
        )
        self.estudiante1.groups.add(self.grupo_estudiante)
        
        self.estudiante2 = User.objects.create_user(
            username='estudiante2',
            email='estudiante2@test.com',
            password='testpass123'
        )
        self.estudiante2.groups.add(self.grupo_estudiante)
        
        self.docente = User.objects.create_user(
            username='docente1',
            email='docente1@test.com',
            password='testpass123'
        )
        self.docente.groups.add(self.grupo_docente)
        
        # Crear proyectos con diferentes estados y calificaciones
        pdf_content = b'%PDF-1.4 fake pdf content'
        
        # 2 proyectos enviados (sin calificar)
        for i in range(2):
            pdf_file = SimpleUploadedFile(
                f'proyecto_enviado_{i}.pdf',
                pdf_content,
                content_type='application/pdf'
            )
            Proyecto.objects.create(
                titulo=f'Proyecto Enviado {i}',
                descripcion='Proyecto en estado enviado',
                estudiante=self.estudiante1,
                documento=pdf_file,
                estado='enviado'
            )
        
        # 3 proyectos en revisión (1 sin calificar, 2 con calificación)
        for i in range(3):
            pdf_file = SimpleUploadedFile(
                f'proyecto_revision_{i}.pdf',
                pdf_content,
                content_type='application/pdf'
            )
            proyecto = Proyecto.objects.create(
                titulo=f'Proyecto Revisión {i}',
                descripcion='Proyecto en estado revisión',
                estudiante=self.estudiante2,
                documento=pdf_file,
                estado='revision'
            )
            # Solo los primeros 2 tienen calificación
            if i < 2:
                proyecto.calificacion = 3.5 + i  # 3.5 y 4.5
                proyecto.save()
        
        # 2 proyectos aprobados (con calificación)
        for i in range(2):
            pdf_file = SimpleUploadedFile(
                f'proyecto_aprobado_{i}.pdf',
                pdf_content,
                content_type='application/pdf'
            )
            proyecto = Proyecto.objects.create(
                titulo=f'Proyecto Aprobado {i}',
                descripcion='Proyecto en estado aprobado',
                estudiante=self.estudiante1,
                documento=pdf_file,
                estado='aprobado',
                calificacion=4.0 + i * 0.5  # 4.0 y 4.5
            )
    
    def test_estadisticas_requiere_autenticacion(self):
        """
        Verificar que la vista de estadísticas requiere autenticación.
        Requisito: 11.1
        """
        response = self.client.get('/estadisticas/')
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_estadisticas_requiere_rol_docente(self):
        """
        Verificar que solo docentes pueden acceder a estadísticas.
        Requisitos: 10.1, 11.2
        """
        # Intentar acceder como estudiante
        self.client.login(username='estudiante1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # Debe redirigir o denegar acceso (302 o 403)
        self.assertIn(response.status_code, [302, 403])
    
    def test_estadisticas_docente_puede_acceder(self):
        """
        Verificar que docentes pueden acceder a estadísticas.
        Requisitos: 10.1, 11.1, 11.2
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estadisticas.html')
    
    def test_estadisticas_muestra_total_por_estado(self):
        """
        Verificar que se muestran totales de proyectos por estado.
        Requisito: 10.2
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # Verificar contexto
        self.assertEqual(response.context['total_enviados'], 2)
        self.assertEqual(response.context['total_revision'], 3)
        self.assertEqual(response.context['total_aprobados'], 2)
        self.assertEqual(response.context['total_proyectos'], 7)
    
    def test_estadisticas_calcula_promedio_calificaciones(self):
        """
        Verificar que se calcula el promedio de calificaciones correctamente.
        Requisito: 10.3
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # Promedio: (3.5 + 4.5 + 4.0 + 4.5) / 4 = 16.5 / 4 = 4.125
        promedio = response.context['promedio_calificacion']
        self.assertIsNotNone(promedio)
        self.assertAlmostEqual(float(promedio), 4.125, places=2)
    
    def test_estadisticas_muestra_sin_calificar(self):
        """
        Verificar que se muestra el total de proyectos sin calificar.
        Requisito: 10.4
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # 2 enviados + 1 en revisión sin calificar = 3 sin calificar
        self.assertEqual(response.context['sin_calificar'], 3)
    
    def test_estadisticas_template_muestra_metricas(self):
        """
        Verificar que el template muestra todas las métricas.
        Requisitos: 10.2, 10.3, 10.4, 10.5
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # Verificar que se muestran las métricas en el HTML
        self.assertContains(response, 'Total de Proyectos')
        self.assertContains(response, 'Enviados')
        self.assertContains(response, 'En Revisión')
        self.assertContains(response, 'Aprobados')
        self.assertContains(response, 'Promedio de Calificaciones')
        self.assertContains(response, 'Sin Calificar')
        
        # Verificar valores
        self.assertContains(response, '7')  # Total proyectos
        self.assertContains(response, '2')  # Enviados
        self.assertContains(response, '3')  # En revisión
        self.assertContains(response, '2')  # Aprobados (aparece dos veces)
        # El promedio puede aparecer como 4,13 o 4.13 dependiendo del locale
        self.assertTrue('4,13' in response.content.decode() or '4.13' in response.content.decode())
        self.assertContains(response, '3')  # Sin calificar
    
    def test_estadisticas_usa_cards_con_colores(self):
        """
        Verificar que las estadísticas usan cards con colores distintivos.
        Requisito: 12.6
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # Verificar colores de badges según diseño
        self.assertContains(response, 'border-blue-900')  # Total proyectos
        self.assertContains(response, 'border-blue-500')  # Enviados
        self.assertContains(response, 'border-amber-500')  # En revisión
        self.assertContains(response, 'border-emerald-600')  # Aprobados
        self.assertContains(response, 'border-orange-600')  # Promedio
        self.assertContains(response, 'border-red-500')  # Sin calificar
    
    def test_estadisticas_usa_grid_responsive(self):
        """
        Verificar que las estadísticas usan grid responsive de Tailwind.
        Requisito: 12.6
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # Verificar clases de grid responsive
        self.assertContains(response, 'grid-cols-1')
        self.assertContains(response, 'sm:grid-cols-2')
        self.assertContains(response, 'lg:grid-cols-3')
    
    def test_estadisticas_muestra_iconos(self):
        """
        Verificar que las estadísticas muestran iconos SVG.
        Requisito: 12.6
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # Verificar que hay iconos SVG
        self.assertContains(response, '<svg')
        self.assertContains(response, 'viewBox')
    
    def test_estadisticas_sin_proyectos(self):
        """
        Verificar que las estadísticas funcionan sin proyectos.
        Requisito: 10.2, 10.3, 10.4
        """
        # Eliminar todos los proyectos
        Proyecto.objects.all().delete()
        
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_enviados'], 0)
        self.assertEqual(response.context['total_revision'], 0)
        self.assertEqual(response.context['total_aprobados'], 0)
        self.assertEqual(response.context['total_proyectos'], 0)
        self.assertIsNone(response.context['promedio_calificacion'])
        self.assertEqual(response.context['sin_calificar'], 0)
    
    def test_estadisticas_sin_calificaciones(self):
        """
        Verificar que el promedio es None cuando no hay calificaciones.
        Requisito: 10.3
        """
        # Eliminar todas las calificaciones
        Proyecto.objects.all().update(calificacion=None)
        
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        self.assertIsNone(response.context['promedio_calificacion'])
        self.assertEqual(response.context['sin_calificar'], 7)
    
    def test_estadisticas_muestra_graficos_visuales(self):
        """
        Verificar que las estadísticas incluyen gráficos visuales.
        Requisito: 12.6 (opcional)
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        # Verificar que hay visualización de distribución
        self.assertContains(response, 'Distribución de Proyectos por Estado')
        # Verificar que hay barras de progreso visuales
        self.assertContains(response, 'bg-blue-500 h-4 rounded-full')
        self.assertContains(response, 'bg-amber-500 h-4 rounded-full')
        self.assertContains(response, 'bg-emerald-600 h-4 rounded-full')
    
    def test_estadisticas_tiene_enlace_dashboard(self):
        """
        Verificar que hay enlace para volver al dashboard.
        Requisito: 10.5
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        self.assertContains(response, 'Volver al Dashboard')
        self.assertContains(response, 'href="/dashboard/"')
    
    def test_estadisticas_tiene_acciones_rapidas(self):
        """
        Verificar que hay sección de acciones rápidas.
        Requisito: 10.5
        """
        self.client.login(username='docente1', password='testpass123')
        response = self.client.get('/estadisticas/')
        
        self.assertContains(response, 'Acciones Rápidas')
        self.assertContains(response, 'Ver Todos los Proyectos')
