import numpy as np
import pandas as pd
from datetime import datetime, timedelta

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
# Probabilidades de asistencia o ausencia
PROB_ASISTENCIA = 0.85  
INJUSTIFICADA = 0.3  
ENFERMEDAD = 0.5
FRANCO = 0.2

#Proporciona minutos de desfase que nos van a servir para horario de ingreso o egreso de una horario
def minutos_random_desfasar(antes, despues):
    return np.random.randint(-antes, despues)

def generar_dataset():

    data = []   # Lista para almacenar los registros

    # Generar datos para cada empleado
    for emp_id in range(1, CANT_EMPLEADOS + 1):
        for fecha in FECHAS:
            dia_semana = fecha.strftime("%A")   # Día de la semana

            if dia_semana not in DIAS_NO_LABORABLES:
                asistencia = np.random.choice([1, 0], p=[PROB_ASISTENCIA, 1 - PROB_ASISTENCIA]) # Asistencia aleatoria

                if asistencia == 1:
                    hora_entrada = (HORA_ENTRADA + timedelta(minutes = minutos_random_desfasar(MIN_LLEGA_ANTES, MIN_LLEGA_TARDE))).strftime("%H:%M")
                    hora_salida = (HORA_SALIDA + timedelta(minutes = minutos_random_desfasar(-MIN_SE_RETIRA_ANTES, MIN_SE_RETIRA_TARDE))).strftime("%H:%M")
                    tipo_ausencia = "Ninguna"
                else:
                    hora_entrada = "-"
                    hora_salida = "-"
                    tipo_ausencia = np.random.choice(["Falta injustificada", "Enfermedad", "Franco"], p=[INJUSTIFICADA, ENFERMEDAD, FRANCO])

                data.append([emp_id, fecha.strftime("%Y-%m-%d"), dia_semana, asistencia, hora_entrada, hora_salida, tipo_ausencia])

    # Convertir a DataFrame
    df = pd.DataFrame(data, columns=["empleado_id", "fecha", "dia_semana", "asistencia", "hora_entrada", "hora_salida", "tipo_ausencia"])

    # Guardar en CSV
    df.to_csv("asistencia_empleados.csv", index=False)
    print("---> Se ha generado el archivo 'asistencia_empleados.csv'")
    return