from __future__ import absolute_import, unicode_literals
from celery.decorators import task
from celery.utils.log import get_task_logger

from macwebapp.models import *

import re
from datetime import datetime
import subprocess, shlex
import os


logger = get_task_logger(__name__)


@task(name="ejecutar_analisis")
def ejecutar_analisis(id_ejecucion):
	""" Ejecución de análisis"""
	logger.info("arranque de ejecución análisis.")

	ejecucion = Ejecucion.objects.get(pk=id_ejecucion)
	loguear('Se ejecutará registro #' + str(ejecucion.id), '')

	ejecucion.fechahora_inicio = datetime.now()
	ejecucion.estado = EJECUCION_ESTADO_EN_PROCESO
	ejecucion.save()

	muestra = ejecucion.muestras.all()[0]
	archivo = muestra.archivo.file.name
	comando = ejecucion.analisis.comando.replace('#archivo#', archivo)

	loguear('Se ejecutará comando: ' + comando, '')

	(stdout, stderr, ret) = ejecutar_cmd(comando)
	if ret != 0 or not stdout:
		loguear('Error al ejecutar comando: ' + comando, stderr)
		return

	regex_resultado = ejecucion.analisis.regex_resultado
	regex_resultado_comparativo = ejecucion.analisis.regex_resultado_comparativo

	try:
		match_r = re.search(regex_resultado, stdout, re.MULTILINE)
		match_rc = re.search(regex_resultado_comparativo, stdout, re.MULTILINE)
		resultado = match_r.group(1)
		resultado_comparativo = match_rc.group(1)
	except:
		loguear('Error al procesar salida de comando: ' + comando, stdout)
		return

	resultado_obj = Resultado(ejecucion=ejecucion, resultado=resultado, resultado_comparativo=resultado_comparativo, salida=stdout, error=False)
	resultado_obj.save()

	ejecucion.fechahora_fin = datetime.now()
	ejecucion.estado = EJECUCION_ESTADO_FINALIZADA
	ejecucion.save()

	loguear('Ejecución exitosa para registro #' + str(ejecucion.id), '')

	logger.info("finalización de ejecución análisis.")


###############################################################################
def ejecutar_cmd(cmd, cwd='/tmp'):
	"""
	Función para la ejecución de comandos a sistema
	"""
	args = shlex.split(cmd)
	p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	(stdout, stderr) = p.communicate()
	return (stdout, stderr, p.returncode)

###############################################################################
def loguear(desc, det):
	bitacora = Bitacora(descripcion=desc, detalles=det)
	bitacora.save()
