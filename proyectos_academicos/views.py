from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from .models import Proyecto, Comentario
from .forms import ProyectoForm, ProyectoDocenteForm, ComentarioForm


@login_required
def dashboard_redirect(request):
    """
    Vista de dashboard diferenciada por rol del usuario.
    Para estudiantes: muestra sus propios proyectos y botón de crear proyecto.
    Para docentes: muestra todos los proyectos y enlace a estadísticas.
    Requisitos: 1.5, 13.3, 13.4, 13.5
    """
    user = request.user

    # Verificar si el usuario es docente
    if user.groups.filter(name='docente').exists():
        # Docentes ven todos los proyectos
        proyectos = Proyecto.objects.all().select_related('estudiante')
        
        return render(request, 'dashboard.html', {
            'user_role': 'docente',
            'proyectos': proyectos,
            'total_proyectos': proyectos.count(),
        })
    
    # Verificar si el usuario es estudiante
    elif user.groups.filter(name='estudiante').exists():
        # Estudiantes solo ven sus propios proyectos
        proyectos = Proyecto.objects.filter(estudiante=user)
        
        return render(request, 'dashboard.html', {
            'user_role': 'estudiante',
            'proyectos': proyectos,
            'total_proyectos': proyectos.count(),
        })
    
    else:
        # Usuario sin rol asignado
        return render(request, 'dashboard.html', {
            'user_role': 'sin_rol',
            'proyectos': [],
            'total_proyectos': 0,
        })


class ProyectoListView(LoginRequiredMixin, ListView):
    """
    Vista de lista de proyectos con filtros por estado y estudiante.
    Requisitos: 7.1, 7.2, 7.3, 7.4, 15.1
    """
    model = Proyecto
    template_name = 'proyectos/proyecto_list.html'
    context_object_name = 'proyectos'
    paginate_by = 10

    def get_queryset(self):
        """
        Filtra proyectos según parámetros GET y rol del usuario.
        """
        queryset = Proyecto.objects.all().select_related('estudiante')
        
        # Si el usuario es estudiante, solo mostrar sus propios proyectos
        if self.request.user.groups.filter(name='estudiante').exists():
            queryset = queryset.filter(estudiante=self.request.user)
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado and estado in ['enviado', 'revision', 'aprobado']:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por estudiante (solo para docentes)
        if self.request.user.groups.filter(name='docente').exists():
            estudiante_id = self.request.GET.get('estudiante')
            if estudiante_id:
                queryset = queryset.filter(estudiante_id=estudiante_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        """
        Agrega información adicional al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['is_docente'] = self.request.user.groups.filter(name='docente').exists()
        context['is_estudiante'] = self.request.user.groups.filter(name='estudiante').exists()
        
        # Pasar parámetros de filtro actuales
        context['current_estado'] = self.request.GET.get('estado', '')
        context['current_estudiante'] = self.request.GET.get('estudiante', '')
        
        # Lista de estudiantes para el filtro (solo docentes)
        if context['is_docente']:
            from django.contrib.auth.models import User
            context['estudiantes'] = User.objects.filter(groups__name='estudiante').order_by('username')
        
        return context


class ProyectoCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear un nuevo proyecto.
    Requisitos: 2.1, 2.2, 15.2
    """
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/proyecto_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """
        Asigna el estudiante automáticamente y establece estado='enviado'.
        """
        form.instance.estudiante = self.request.user
        form.instance.estado = 'enviado'
        # fecha_envio se establece automáticamente con auto_now_add
        
        messages.success(self.request, 'Proyecto creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Nuevo Proyecto'
        context['button_text'] = 'Crear Proyecto'
        return context


class ProyectoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vista para editar un proyecto existente con control de acceso.
    Requisitos: 2.3, 2.4, 2.7, 4.2, 4.3, 11.4, 11.5, 15.3
    """
    model = Proyecto
    template_name = 'proyectos/proyecto_form.html'

    def get_form_class(self):
        """
        Retorna el formulario apropiado según el rol del usuario.
        """
        if self.request.user.groups.filter(name='docente').exists():
            return ProyectoDocenteForm
        return ProyectoForm

    def get_success_url(self):
        return reverse_lazy('proyecto_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        """
        Verifica permisos de edición:
        - Estudiante: solo sus propios proyectos Y estado != 'aprobado'
        - Docente: cualquier proyecto
        """
        proyecto = self.get_object()
        user = self.request.user
        
        # Docente puede editar cualquier proyecto
        if user.groups.filter(name='docente').exists():
            return True
        
        # Estudiante solo puede editar sus propios proyectos no aprobados
        if user.groups.filter(name='estudiante').exists():
            return proyecto.estudiante == user and proyecto.estado != 'aprobado'
        
        return False

    def form_valid(self, form):
        """
        Actualiza fecha_revision cuando el estado cambia a 'revision' o 'aprobado'.
        """
        # Verificar si el estado cambió a 'revision' o 'aprobado'
        if 'estado' in form.changed_data:
            if form.instance.estado in ['revision', 'aprobado']:
                form.instance.fecha_revision = timezone.now()
        
        messages.success(self.request, 'Proyecto actualizado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Proyecto'
        context['button_text'] = 'Guardar Cambios'
        context['is_update'] = True
        return context


class ProyectoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Vista para eliminar un proyecto con restricciones.
    Requisitos: 2.5, 2.6, 11.4, 11.5, 15.4
    """
    model = Proyecto
    template_name = 'proyectos/proyecto_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        """
        Verifica permisos de eliminación:
        - Solo el propietario puede eliminar
        - Solo si el estado es 'enviado'
        """
        proyecto = self.get_object()
        user = self.request.user
        
        return (
            proyecto.estudiante == user and 
            proyecto.estado == 'enviado'
        )

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Proyecto eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class ProyectoDetailView(LoginRequiredMixin, DetailView):
    """
    Vista de detalle de proyecto con comentarios.
    Requisitos: 14.1, 14.2, 14.3, 14.4, 14.5, 15.5
    """
    model = Proyecto
    template_name = 'proyectos/proyecto_detail.html'
    context_object_name = 'proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = self.object
        
        # Obtener comentarios ordenados por fecha
        context['comentarios'] = proyecto.comentarios.all().select_related('usuario')
        
        # Verificar si se puede agregar comentarios
        context['puede_comentar'] = proyecto.estado != 'aprobado'
        
        # Formulario de comentario si se puede comentar
        if context['puede_comentar']:
            context['comentario_form'] = ComentarioForm()
        
        # Verificar permisos de edición y eliminación
        user = self.request.user
        context['puede_editar'] = False
        context['puede_eliminar'] = False
        
        if user.groups.filter(name='docente').exists():
            context['puede_editar'] = True
        elif user.groups.filter(name='estudiante').exists():
            if proyecto.estudiante == user:
                context['puede_editar'] = proyecto.estado != 'aprobado'
                context['puede_eliminar'] = proyecto.estado == 'enviado'
        
        context['is_docente'] = user.groups.filter(name='docente').exists()
        context['is_estudiante'] = user.groups.filter(name='estudiante').exists()
        
        return context


class ComentarioCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear comentarios en proyectos.
    Requisitos: 5.1, 5.2, 5.4, 5.5, 15.6
    """
    model = Comentario
    form_class = ComentarioForm
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica que el proyecto exista y permita comentarios.
        """
        self.proyecto = get_object_or_404(Proyecto, pk=kwargs['proyecto_pk'])
        
        # Verificar que el proyecto no esté aprobado
        if self.proyecto.estado == 'aprobado':
            messages.error(request, 'No se pueden agregar comentarios a proyectos aprobados.')
            return redirect('proyecto_detail', pk=self.proyecto.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Asigna el usuario y proyecto automáticamente.
        """
        form.instance.usuario = self.request.user
        form.instance.proyecto = self.proyecto
        
        messages.success(self.request, 'Comentario agregado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('proyecto_detail', kwargs={'pk': self.proyecto.pk})


def es_docente(user):
    """
    Helper function para verificar si un usuario es docente.
    """
    return user.groups.filter(name='docente').exists()


@login_required
@user_passes_test(es_docente)
def estadisticas_view(request):
    """
    Vista de panel de estadísticas para docentes.
    Muestra métricas agregadas de proyectos.
    Requisitos: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2
    """
    # Calcular total de proyectos por estado
    total_enviados = Proyecto.objects.filter(estado='enviado').count()
    total_revision = Proyecto.objects.filter(estado='revision').count()
    total_aprobados = Proyecto.objects.filter(estado='aprobado').count()
    
    # Calcular promedio de calificaciones
    promedio_calificacion = Proyecto.objects.filter(
        calificacion__isnull=False
    ).aggregate(Avg('calificacion'))['calificacion__avg']
    
    # Calcular total de proyectos sin calificar
    sin_calificar = Proyecto.objects.filter(calificacion__isnull=True).count()
    
    # Total de proyectos
    total_proyectos = Proyecto.objects.count()
    
    # Pasar estadísticas al template
    context = {
        'total_enviados': total_enviados,
        'total_revision': total_revision,
        'total_aprobados': total_aprobados,
        'promedio_calificacion': promedio_calificacion,
        'sin_calificar': sin_calificar,
        'total_proyectos': total_proyectos,
    }
    
    return render(request, 'estadisticas.html', context)
