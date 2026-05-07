from django.apps import AppConfig


class ProyectosAcademicosConfig(AppConfig):
    name = 'proyectos_academicos'
    
    def ready(self):
        """
        Importar signals cuando la aplicación esté lista.
        Requisitos: 6.1
        """
        import proyectos_academicos.signals
