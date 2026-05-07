from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Proyecto, Comentario


class ProyectoForm(forms.ModelForm):
    """
    Formulario para crear y editar proyectos.
    Usa django-crispy-forms con Tailwind CSS.
    Requisitos: 12.2, 15.2, 15.3
    """

    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'documento']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'titulo': 'Título del Proyecto',
            'descripcion': 'Descripción',
            'documento': 'Documento PDF',
        }
        help_texts = {
            'documento': 'Solo se permiten archivos PDF.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-4'


class ProyectoDocenteForm(forms.ModelForm):
    """
    Formulario para que docentes editen proyectos.
    Incluye campos de estado y calificación.
    Requisitos: 4.2, 4.3, 15.3
    """

    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'documento', 'estado', 'calificacion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'titulo': 'Título del Proyecto',
            'descripcion': 'Descripción',
            'documento': 'Documento PDF',
            'estado': 'Estado',
            'calificacion': 'Calificación (0.0 - 5.0)',
        }
        help_texts = {
            'documento': 'Solo se permiten archivos PDF.',
            'calificacion': 'Ingrese una calificación entre 0.0 y 5.0',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-4'


class ComentarioForm(forms.ModelForm):
    """
    Formulario para crear comentarios en proyectos.
    Requisitos: 12.2, 15.6
    """

    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu comentario aquí...'}),
        }
        labels = {
            'texto': 'Comentario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-4'
