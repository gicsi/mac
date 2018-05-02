from django.db import models

###############################################################################

EJECUCION_ESTADO_PENDIENTE = '1'
EJECUCION_ESTADO_EN_PROCESO = '2'
EJECUCION_ESTADO_FINALIZADA = '3'
EJECUCION_ESTADO_CHOICES = (
    (EJECUCION_ESTADO_PENDIENTE, 'PENDIENTE'),
    (EJECUCION_ESTADO_EN_PROCESO, 'EN PROCESO'),
    (EJECUCION_ESTADO_FINALIZADA, 'FINALIZADA'),
)

EXPRESADO_EN_BINARIO = '1'
EXPRESADO_EN_OCTAL = '2'
EXPRESADO_EN_DECIMAL = '3'
EXPRESADO_EN_HEXADECIMAL = '4'
EXPRESADO_EN_ASCII = '5'
EXPRESADO_EN_CHOICES = (
    (EXPRESADO_EN_BINARIO, 'BINARIO'),
    (EXPRESADO_EN_OCTAL, 'OCTAL'),
    (EXPRESADO_EN_DECIMAL, 'DECIMAL'),
    (EXPRESADO_EN_HEXADECIMAL, 'HEXADECIMAL'),
    (EXPRESADO_EN_ASCII, 'ASCII'),
)

###############################################################################

class TipoMuestra(models.Model):
    nombre = models.CharField(verbose_name='nombre', help_text='Nombre de referencia', max_length=255, unique=True)
    descripcion = models.TextField(verbose_name='descripción', help_text='Descripción detallada', blank=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = 'tipo de muestra'
        verbose_name_plural = 'tipos de muestras'
    def __str__(self):
        return self.nombre

class Muestra(models.Model):
    tipo_muestra = models.ForeignKey(TipoMuestra, verbose_name='tipo de muestra', help_text='Tipo de muestra', related_name='muestras', on_delete=models.CASCADE)
    nombre = models.CharField(verbose_name='nombre', help_text='Nombre de referencia', max_length=255, unique=True)
    descripcion = models.TextField(verbose_name='descripción', help_text='Descripción detallada', blank=True)
    valor = models.TextField(verbose_name='valor', help_text='Valor o contenido (completar si no se selecciona Archivo)', blank=True)
    archivo = models.FileField(verbose_name='archivo', help_text='Archivo de la muestra (seleccionar si no se completa Valor/Contenido)', blank=True, upload_to='muestras/')
    expresado_en =  models.CharField(verbose_name='expresado en', help_text='Expresado en ...', max_length=2, choices=EXPRESADO_EN_CHOICES, default=EXPRESADO_EN_BINARIO)
    class Meta:
        ordering = ['nombre']
        verbose_name = 'muestra'
        verbose_name_plural = 'muestras'
    def __str__(self):
        return self.nombre

class TipoAnalisis(models.Model):
    nombre = models.CharField(verbose_name='nombre', help_text='Nombre de referencia', max_length=255, unique=True)
    descripcion = models.TextField(verbose_name='descripción', help_text='Descripción detallada', blank=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = 'tipo de análisis'
        verbose_name_plural = 'tipos de análisis'
    def __str__(self):
        return self.nombre

class Analisis(models.Model):
    tipo_analisis = models.ForeignKey(TipoAnalisis, verbose_name='tipo de análisis', help_text='Tipo o clase de análisis (plugin)', related_name='analisis', on_delete=models.CASCADE)
    nombre = models.CharField(verbose_name='nombre', help_text='Nombre de referencia', max_length=255, unique=True)
    descripcion = models.TextField(verbose_name='descripción', help_text='Descripción detallada', blank=True)
    comando = models.CharField(verbose_name='comando', help_text='Comando a ejecutar (encerrar parámetros entre #, por ej.: /var/foo/test #archivo#)', max_length=255, default='')
    regex_resultado = models.CharField(verbose_name='expresión regular para resultado', help_text='Expresión regular para obtener valor de resultado', max_length=255)
    regex_resultado_comparativo = models.CharField(verbose_name='expresión regular para resultado comparativo', help_text='Expresión regular para obtener valor de resultado comparativo', max_length=255)
    descripcion_resultado = models.CharField(verbose_name='descripción de resultado', help_text='Descripción, nombre o etiqueta del valor de resultado', max_length=255, default='')
    class Meta:
        ordering = ['nombre']
        verbose_name = 'análisis'
        verbose_name_plural = 'análisis'
    def __str__(self):
        return self.nombre

class Ejecucion(models.Model):
    analisis = models.ForeignKey(Analisis, verbose_name='análisis', help_text='Análisis a ejecutar', related_name='ejecuciones', on_delete=models.CASCADE)
    estado =  models.CharField(verbose_name='estado', help_text='Estado de la ejecución', max_length=2, choices=EJECUCION_ESTADO_CHOICES, default=EJECUCION_ESTADO_PENDIENTE)
    fechahora_inicio = models.DateTimeField(verbose_name='fecha de inicio', help_text='Fecha y hora de inicio de la ejecución del análisis', blank=True, null=True)
    fechahora_fin = models.DateTimeField(verbose_name='fecha de finalización', help_text='Fecha y hora de finalización de la ejecución del análisis', blank=True, null=True)
    muestras = models.ManyToManyField(Muestra, verbose_name='muestras', help_text='Muestras para la ejecución', related_name='ejecuciones')
    class Meta:
        ordering = ['analisis']
        verbose_name = 'ejecución'
        verbose_name_plural = 'ejecuciones'
    def __str__(self):
        return self.analisis.nombre + ' - ' + self.get_estado_display()

class Resultado(models.Model):
    ejecucion = models.ForeignKey(Ejecucion, verbose_name='ejecución', help_text='Ejecución de análisis', related_name='resultados', on_delete=models.CASCADE)
    resultado = models.CharField(verbose_name='resultado', help_text='Resultado de la ejecución', max_length=255)
    resultado_comparativo = models.CharField(verbose_name='resultado comparativo', help_text='Resultado comparativo de la ejecución', max_length=255)
    salida = models.TextField(verbose_name='salida', help_text='Salida completa de ejecución de análisis')
    error = models.BooleanField(verbose_name='error', help_text='Se produjo un error al ejecutar?', default=False)
    class Meta:
        ordering = ['ejecucion']
        verbose_name = 'resultado'
        verbose_name_plural = 'resultados'
    def __str__(self):
        return self.resultado

class Bitacora(models.Model):
    fechahora = models.DateTimeField(verbose_name='fecha y hora', help_text='Fecha y hora del registro', blank=False, auto_now_add=True)
    descripcion = models.CharField(verbose_name='descripción', help_text='Descripción del registro', max_length=255)
    detalles = models.TextField(verbose_name='detalles', help_text='Detalles del registro', blank=True)
    class Meta:
        ordering = ['fechahora']
        verbose_name = 'bitácora'
        verbose_name_plural = 'bitácoras'
    def __str__(self):
        return self.fechahora + ' - ' + self.descripcion
