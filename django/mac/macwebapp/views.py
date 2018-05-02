from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from material.frontend.views import ModelViewSet

from . import models
from macwebapp.tasks import ejecutar_analisis

from django.db.models import Q
from functools import reduce
from operator import or_



class ModelViewSetWithFilter(ModelViewSet):
    def get_queryset(self, request):
        queryset = self.model._default_manager.all()
        srch = request.GET.get('datatable-search[value]', '')
        if srch:
            kwargs = {}
            #field_names = [f.name for f in self.model._meta.get_fields()]
            for field_name in self.list_filterset_fields:
                kwargs['{0}__{1}'.format(field_name, 'icontains')] = srch
            list_of_Q = [Q(**{key: val}) for key, val in kwargs.items()]
            return queryset.filter(reduce(or_, list_of_Q))
        return queryset


class TipoAnalisisModelViewSet(ModelViewSetWithFilter):
    model = models.TipoAnalisis
    list_display = ['nombre', 'descripcion']
    list_filterset_fields = ['nombre', 'descripcion']

class TipoMuestraModelViewSet(ModelViewSetWithFilter):
    model = models.TipoMuestra
    list_display = ['nombre', 'descripcion']
    list_filterset_fields = ['nombre', 'descripcion']

class AnalisisModelViewSet(ModelViewSetWithFilter):
    model = models.Analisis
    list_display = ['nombre', 'tipo_analisis', 'descripcion']
    list_filterset_fields = ['tipo_analisis__nombre', 'nombre', 'descripcion']

class MuestraModelViewSet(ModelViewSetWithFilter):
    model = models.Muestra
    list_display = ['nombre', 'tipo_muestra', 'descripcion']
    list_filterset_fields = ['tipo_muestra__nombre', 'nombre', 'descripcion']

class EjecucionModelViewSet(ModelViewSetWithFilter):
    model = models.Ejecucion
    list_display = ['analisis', 'muestras__', 'fechahora_inicio', 'fechahora_fin', 'estado__', 'acciones']
    list_filterset_fields = ['analisis__nombre', 'fechahora_inicio', 'fechahora_fin']
    def muestras__(self, obj):
        return "\n".join([m.nombre for m in obj.muestras.all()])
    def estado__(self, obj):
        return obj.get_estado_display()
    def acciones(self, obj):
        return '<a href="../ejecutar/' + str(obj.id) + '/"><i class="material-icons">play_circle_filled</i></a>'
    acciones.short_description = ''

class ResultadoModelViewSet(ModelViewSetWithFilter):
    model = models.Resultado
    list_display = ['ejecucion__analisis__descripcion_resultado', 'resultado', 'ejecucion__analisis__nombre', 'ejecucion__muestras__nombre', 'ejecucion__fechahora_fin', 'error']
    list_filterset_fields = ['resultado']
    list_display_links = ['resultado']
    def ejecucion__fechahora_fin(self, obj):
        return obj.ejecucion.fechahora_fin
    ejecucion__fechahora_fin.short_description = 'Finalizado'
    def ejecucion__analisis__nombre(self, obj):
        return obj.ejecucion.analisis.nombre
    ejecucion__analisis__nombre.short_description = 'Análisis'
    def ejecucion__analisis__descripcion_resultado(self, obj):
        return obj.ejecucion.analisis.descripcion_resultado
    ejecucion__analisis__descripcion_resultado.short_description = ''
    def ejecucion__muestras__nombre(self, obj):
        return obj.ejecucion.muestras.all()[0].nombre
    ejecucion__muestras__nombre.short_description = 'Muestras'


class BitacoraModelViewSet(ModelViewSetWithFilter):
    model = models.Bitacora
    list_display = ['fechahora', 'descripcion', 'detalles']
    list_filterset_fields = ['fechahora', 'descripcion', 'detalles']
    list_display_links = [None]
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request):
        return False
 
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "macwebapp/index.html"

class ReportesView(LoginRequiredMixin, TemplateView):
    template_name = "macwebapp/reportes.html"

class ComparativasView(LoginRequiredMixin, TemplateView):
    template_name = "macwebapp/comparativas.html"

class EjecutarView(LoginRequiredMixin, TemplateView):
    template_name = "macwebapp/ejecutar.html"
    def get_context_data(self, **kwargs):
        context = super(EjecutarView, self).get_context_data(**kwargs)
        id = int(self.kwargs.get('id'))
        ejecutar_analisis.delay(id)
        #context['id'] = id
        #context['tmp'] = 'id: ' + self.kwargs.get('id')
        context['tmp'] = ''
        return context
