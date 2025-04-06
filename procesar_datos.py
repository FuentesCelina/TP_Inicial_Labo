import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def pre_procesar_datos(archivo):
    """Carga el dataset de asistencia desde un archivo CSV y lo prepara para el análisis."""
    df = pd.read_csv(archivo)

    # Convertir horas a minutos para análisis numérico
    df['min_entrada'] = df['hora_entrada'].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if x != "-" else np.nan)
    df['min_salida'] = df['hora_salida'].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if x != "-" else np.nan)

    # Convertir a categorías numéricas
    df['dia_semana'] = df['dia_semana'].astype('category').cat.codes
    df['tipo_ausencia'] = df['tipo_ausencia'].astype('category').cat.codes

    # Rellenar valores nulos
    df.fillna(-1, inplace=True)

    # Crear nuevas características
    df['faltas_acumuladas'] = df.groupby('empleado_id')['asistencia'].transform(lambda x: (x == 0).sum())
    df['faltas_seguidas'] = df.groupby('empleado_id')['asistencia'].transform(lambda x: x.eq(0).astype(int).groupby(x.ne(0).cumsum()).cumsum().max())
    df['falta_lunes_viernes'] = df.apply(lambda row: 1 if row['dia_semana'] in [0, 4] and row['asistencia'] == 0 else 0, axis=1)
    # llegada_tarde ahora contabiliza cuántos minutos tardó
    df['llegada_tarde'] = df['min_entrada'].apply(lambda x: x - 480 if x > 485 and x != -1 else 0)  # Suponiendo 8:05 AM como horario tope normal de llegada
    # retiro_temprano ahora contabiliza cuántos minutos se fue antes
    df['retiro_temprano'] = df['min_salida'].apply(lambda x: 1020 - x if x < 1015 and x != -1 else 0)  # Suponiendo 4:55 PM como salida anticipada normal

    # Eliminar características ya procesadas
    df.drop(['fecha', 'dia_semana', 'asistencia', 'hora_entrada', 'hora_salida', 'min_entrada', 'min_salida'], axis = 1, inplace = True)

    # Reprocesar nuevas columnas
    # - suma todas las inasistencias de los lunes y los viernes
    # - suma todos los minutos no trabajados y los transforma a horas
    df['falta_lunes_viernes'] = df.groupby('empleado_id')['falta_lunes_viernes'].transform(lambda x: (x == 1).sum())
    df['llegada_tarde'] = (df.groupby('empleado_id')['llegada_tarde'].transform('sum') // 60).astype(int)
    df['retiro_temprano'] = (df.groupby('empleado_id')['retiro_temprano'].transform('sum') // 60).astype(int)

    return df

def resumir_datos_asistencia(df):
    """Genera un resumen de asistencia por empleado, devuelve un DF procesado y lo guarda en un archivo CSV."""
    resumen = df.groupby('empleado_id').agg(
        faltas_acumuladas=('faltas_acumuladas', 'max'),
        faltas_seguidas=('faltas_seguidas', 'max'),
        falta_lunes_viernes=('falta_lunes_viernes', 'max'),
        llegada_tarde=('llegada_tarde', 'max'),
        retiro_temprano=('retiro_temprano', 'max')
    ).reset_index()

    resumen.to_csv('resumen_de_asistencia.csv', index=False)
    print("---> Archivo 'resumen_de_asistencia.csv' generado correctamente.")

    return resumen

##def detectar_peores_empleados(df, porcentaje, archivo_destino):
##    """Detecta el peor segmento de empleados con asistencia anómala y genera un archivo CSV."""
##
##    # Seleccionar las características relevantes para el análisis
##    X = df[['faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']]
##
##    # Entrenar Isolation Forest para detectar anomalías
##    model = IsolationForest(contamination = porcentaje / 100, random_state=42)
##    model.fit(X)
##
##    # Obtener las puntuaciones de anomalía
##    df['anomaly_score'] = model.decision_function(X)
##
##    # Seleccionar los empleados con peor score (más negativos son más anómalos)
##    df_peores = df.nsmallest(porcentaje, 'anomaly_score')
##
##    # Guardar el resultado en un nuevo archivo CSV
##    df_peores.to_csv(archivo_destino, index=False)
##
##    print("----> Se ha generado '{archivo_destino}' con los empleados más incumplidores.")

def detectar_peores_empleados(df, porcentaje, archivo_destino):
    """
    Detecta el peor segmento de empleados con asistencia anómala y genera un archivo CSV.
    Parámetros:
    - df: dataFrame a trabajar
    - porcentaje: porcentaje de empleados a marcar como más anómalos
    - archivo_destino: ruta del archivo de salida
    """

    n_estimators = 100
    max_samples = 256
    max_features = 1.0
   # max_depth = 8 # IsolationForest no lo acepta
    random_state = 42

    # Seleccionar las características relevantes para el análisis
    X = df[['faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']]

    # Entrenar Isolation Forest con parámetros ajustables
    model = IsolationForest(
        contamination = porcentaje / 100,
        max_samples = max_samples,
        max_features = max_features,
        n_estimators = n_estimators,
        random_state = random_state
    )
    model.fit(X)

    # Obtener las puntuaciones de anomalía
    df['anomaly_score'] = model.decision_function(X)

    # Seleccionar los empleados con peor score (más negativos = más anómalos)
    df_peores = df.nsmallest(int(len(df) * (porcentaje / 100)), 'anomaly_score')

    # Guardar el resultado
    df_peores.to_csv(archivo_destino, index=False)
    print(f"----> Se ha generado '{archivo_destino}' con los empleados más incumplidores.")
