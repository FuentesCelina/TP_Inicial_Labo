import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def _minutos_random_desfasar(desde, hasta):
    return np.random.randint(desde, hasta + 1)

def agregar_anomalias(archivo="asistencia_empleados.csv"):
    """Sobreescribe el archivo de asistencia agregando anomalías específicas."""

    # Cargar el archivo CSV
    df = pd.read_csv(archivo)

    # Probabilidades de incumplimiento (0 - 1)
    prob_llegada_tarde = 0.05
    prob_salida_temprano = 0.05
    prob_faltas_consecutivas = 0.03
    prob_faltar_lunes_viernes = 0.05

    # Horario de entrada y salida
    HORA_ENTRADA = datetime.strptime("08:00", "%H:%M")
    HORA_SALIDA = datetime.strptime("17:00", "%H:%M")

    # Tolerancia y inutos máximos de incumplimiento horario
    MINUTOS_TOLERANCIA = 5
    MINUTOS_LLEGA_TARDE = 90
    MINUTOS_SE_RETIRA_ANTES = 90

    # Convertir a formato datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Anomalía 1: Empleados con llegadas demasiado tarde
    for index, row in df.iterrows():
        if row['asistencia'] == 1 and np.random.rand() < prob_llegada_tarde:
            #df.at[index, 'hora_entrada'] = (datetime.strptime("09:30", "%H:%M")).strftime("%H:%M")
            df.at[index, 'hora_entrada'] = (HORA_ENTRADA + timedelta(minutes = _minutos_random_desfasar(MINUTOS_TOLERANCIA + 1, MINUTOS_LLEGA_TARDE))).strftime("%H:%M")


    # Anomalía 2: Empleados con salidas extremadamente temprano
    for index, row in df.iterrows():
        if row['asistencia'] == 1 and np.random.rand() < prob_salida_temprano:
            #df.at[index, 'hora_salida'] = (datetime.strptime("15:00", "%H:%M")).strftime("%H:%M")
            df.at[index, 'hora_salida'] = (HORA_SALIDA - timedelta(minutes = _minutos_random_desfasar(MINUTOS_TOLERANCIA + 1, MINUTOS_SE_RETIRA_ANTES))).strftime("%H:%M")

    # Anomalía 3: Faltas consecutivas de 5 a 10 días
    empleados = df['empleado_id'].unique()
    num_empleados_anomalos = int(len(empleados) * prob_faltas_consecutivas)
    empleados_anomalos = np.random.choice(empleados, num_empleados_anomalos, replace=False)

    for emp in empleados_anomalos:
        fechas_faltas = df[df['empleado_id'] == emp]['fecha'].sample(1).values[0]
        dias_faltas = np.random.randint(5, 11)
        fechas_a_modificar = pd.date_range(fechas_faltas, periods=dias_faltas)
        df.loc[(df['empleado_id'] == emp) & (df['fecha'].isin(fechas_a_modificar)), ['asistencia', 'hora_entrada', 'hora_salida', 'tipo_ausencia']] = [0, '-', '-', 'Falta injustificada']

    # Anomalía 4: Empleados que faltan siempre los lunes o viernes
    for emp in empleados:
        if np.random.rand() < prob_faltar_lunes_viernes:
            dia_falta = np.random.choice(['Monday', 'Friday'])
            df.loc[(df['empleado_id'] == emp) & (df['dia_semana'] == dia_falta), ['asistencia', 'hora_entrada', 'hora_salida', 'tipo_ausencia']] = [0, '-', '-', 'Alarga fin de semana']

    # Sobreescribe el archivo
    df.to_csv(archivo, index=False)
    print(f"---> Se han agregado anomalías al archivo '{archivo}'")