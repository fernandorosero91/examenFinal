from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_redirect(request):
    """
    Vista temporal de dashboard que redirige según el rol del usuario.
    Esta es una implementación placeholder hasta que se implemente el dashboard completo en la tarea 6.
    Requisitos: 1.3
    """
    user = request.user

    # Verificar si el usuario es docente
    if user.groups.filter(name='docente').exists():
        # Por ahora, renderizar un template simple
        return render(request, 'dashboard.html', {
            'user_role': 'docente',
            'message': 'Bienvenido, Docente. El dashboard completo se implementará en la tarea 6.'
        })
    # Verificar si el usuario es estudiante
    elif user.groups.filter(name='estudiante').exists():
        return render(request, 'dashboard.html', {
            'user_role': 'estudiante',
            'message': 'Bienvenido, Estudiante. El dashboard completo se implementará en la tarea 6.'
        })
    else:
        # Usuario sin rol asignado
        return render(request, 'dashboard.html', {
            'user_role': 'sin_rol',
            'message': 'No tienes un rol asignado. Contacta al administrador.'
        })
