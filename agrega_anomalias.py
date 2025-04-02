import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Probabilidades y parámetros
PROB_LLEGADA_TARDE=PROB_SALIDA_TEMPRANO=PROB_FALTAR_LUNES_VIERNES=0.05
PROB_FALTAS_CONSECUTIVAS=0.03

#Modifica el archivo de asistencia agregando anomalías específicas
def agregar_anomalias(archivo="asistencia_empleados.csv"):

    # Cargar el archivo CSV
    df = pd.read_csv(archivo)

    # Convertir a formato datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    # Anomalía 1: Empleados con llegadas demasiado tarde
    for index, row in df.iterrows():
        if row['asistencia'] == 1 and np.random.rand() < PROB_LLEGADA_TARDE:
            df.at[index, 'hora_entrada'] = (datetime.strptime("09:30", "%H:%M")).strftime("%H:%M")

    # Anomalía 2: Empleados con salidas extremadamente temprano
    for index, row in df.iterrows():
        if row['asistencia'] == 1 and np.random.rand() < PROB_SALIDA_TEMPRANO:
            df.at[index, 'hora_salida'] = (datetime.strptime("15:00", "%H:%M")).strftime("%H:%M")

    # Anomalía 3: Faltas consecutivas de 5 a 10 días
    empleados = df['empleado_id'].unique()
    num_empleados_anomalos = int(len(empleados) * PROB_FALTAS_CONSECUTIVAS)
    empleados_anomalos = np.random.choice(empleados, num_empleados_anomalos, replace=False)

    for emp in empleados_anomalos:
        fechas_faltas = df[df['empleado_id'] == emp]['fecha'].sample(1).values[0]
        dias_faltas = np.random.randint(5, 11)
        fechas_a_modificar = pd.date_range(fechas_faltas, periods=dias_faltas)
        df.loc[(df['empleado_id'] == emp) & (df['fecha'].isin(fechas_a_modificar)), ['asistencia', 'hora_entrada', 'hora_salida', 'tipo_ausencia']] = [0, '-', '-', 'Falta injustificada']

    # Anomalía 4: Empleados que faltan siempre los lunes o viernes
    for emp in empleados:
        if np.random.rand() < PROB_FALTAR_LUNES_VIERNES:
            dia_falta = np.random.choice(['Monday', 'Friday'])
            df.loc[(df['empleado_id'] == emp) & (df['dia_semana'] == dia_falta), ['asistencia', 'hora_entrada', 'hora_salida', 'tipo_ausencia']] = [0, '-', '-', 'Alarga fin de semana']

    # Guardar cambios en el mismo archivo
    df.to_csv(archivo, index=False)
    print(f"---> Se han agregado anomalías al archivo '{archivo}'")