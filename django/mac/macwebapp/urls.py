from django.conf.urls import url, include
from django.views import generic
from . import views


urlpatterns = [
    url('^$', views.IndexView.as_view(), name="index"),
    url('^tipomuestras/', include(views.TipoMuestraModelViewSet().urls)),
    url('^muestras/', include(views.MuestraModelViewSet().urls)),
    url('^tipoanalisis/', include(views.TipoAnalisisModelViewSet().urls)),
    url('^analisis/', include(views.AnalisisModelViewSet().urls)),
    url('^ejecuciones/', include(views.EjecucionModelViewSet().urls)),
    url('^resultados/', include(views.ResultadoModelViewSet().urls)),
    url('^reportes/', views.ReportesView.as_view()),
    url('^comparativas/', views.ComparativasView.as_view()),
    url('^bitacora/', include(views.BitacoraModelViewSet().urls)),
    url('^ejecutar/(?P<id>\d+)/$', views.EjecutarView.as_view()),
]
