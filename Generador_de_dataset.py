#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      jorge
#
# Created:     29/03/2025
# Copyright:   (c) jorge 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def minutos_random_desfasar(antes, despues):
    return np.random.randint(-antes, despues)

# Cantidad de empleados
CANT_EMPLEADOS = 100
# Cantidad de días corridos, fecha de inicio, días que no se trabaja
CANT_DIAS = 120
FECHAS = pd.date_range(start="2025-01-01", periods=CANT_DIAS)
DIAS_NO_LABORABLES = ['Saturday', 'Sunday']

# Horario de entrada y salida
HORA_ENTRADA = datetime.strptime("08:00", "%H:%M")
HORA_SALIDA = datetime.strptime("17:00", "%H:%M")

# Tolerancias normales en minutos
MIN_LLEGA_ANTES = 15
MIN_SE_RETIRA_ANTES = 5
MIN_LLEGA_TARDE = 5
MIN_SE_RETIRA_TARDE = 15

# Proporciones
PROB_ASISTENCIA = 0.85  # Probabilidad de que un empleado asista

INJUSTIFICADA = 0.3  # Causas de inasistencia
ENFERMEDAD = 0.5
FRANCO = 0.2

# Lista para almacenar los registros
data = []

# Generar datos para cada empleado
for emp_id in range(1, CANT_EMPLEADOS + 1):
    faltas_consecutivas = 0  # Contador de faltas seguidas
    for fecha in FECHAS:
        dia_semana = fecha.strftime("%A")  # Día de la semana

        if dia_semana not in DIAS_NO_LABORABLES:
            asistencia = np.random.choice([1, 0], p=[PROB_ASISTENCIA, 1 - PROB_ASISTENCIA])  # Asistencia aleatoria

            if asistencia == 1:
                hora_entrada = (HORA_ENTRADA + timedelta(minutes = minutos_random_desfasar(MIN_LLEGA_ANTES, MIN_LLEGA_TARDE))).strftime("%H:%M")
                hora_salida = (HORA_SALIDA + timedelta(minutes = minutos_random_desfasar(-MIN_SE_RETIRA_ANTES, MIN_SE_RETIRA_TARDE))).strftime("%H:%M")
                tipo_ausencia = "Ninguna"
                faltas_consecutivas = 0  # Reiniciar el contador
            else:
                hora_entrada = "-"
                hora_salida = "-"
                tipo_ausencia = np.random.choice(["Falta injustificada", "Enfermedad", "Franco"], p=[INJUSTIFICADA, ENFERMEDAD, FRANCO])
                faltas_consecutivas += 1  # Aumentar el contador

            data.append([emp_id, fecha.strftime("%Y-%m-%d"), dia_semana, asistencia, hora_entrada, hora_salida, tipo_ausencia, faltas_consecutivas])

# Convertir a DataFrame
df = pd.DataFrame(data, columns=["empleado_id", "fecha", "dia_semana", "asistencia", "hora_entrada", "hora_salida", "tipo_ausencia", "faltas_consecutivas"])

# Mostrar las primeras filas
print(df.head())

# Guardar en CSV
df.to_csv("asistencia_empleados.csv", index=False)