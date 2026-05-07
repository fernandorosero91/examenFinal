from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Proyecto


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
