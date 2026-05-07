from django.urls import path
from . import views

urlpatterns = [
    # Lista de proyectos
    path('proyectos/', views.ProyectoListView.as_view(), name='proyecto_list'),
    
    # Crear proyecto
    path('proyectos/crear/', views.ProyectoCreateView.as_view(), name='proyecto_create'),
    
    # Detalle de proyecto
    path('proyectos/<int:pk>/', views.ProyectoDetailView.as_view(), name='proyecto_detail'),
    
    # Editar proyecto
    path('proyectos/<int:pk>/editar/', views.ProyectoUpdateView.as_view(), name='proyecto_update'),
    
    # Eliminar proyecto
    path('proyectos/<int:pk>/eliminar/', views.ProyectoDeleteView.as_view(), name='proyecto_delete'),
    
    # Crear comentario
    path('proyectos/<int:proyecto_pk>/comentarios/crear/', views.ComentarioCreateView.as_view(), name='comentario_create'),
]
