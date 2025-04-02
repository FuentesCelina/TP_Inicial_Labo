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
    df['llegada_tarde'] = df['min_entrada'].apply(lambda x: 1 if x > 485 and x != -1 else 0)  # Suponiendo 8:05 AM como horario tope normal de llegada
    df['retiro_temprano'] = df['min_salida'].apply(lambda x: 1 if x < 1015 and x != -1 else 0)  # Suponiendo 4:55 PM como salida anticipada normal

    # Eliminar características ya procesadas
    df.drop(['fecha', 'dia_semana', 'asistencia', 'hora_entrada', 'hora_salida', 'min_entrada', 'min_salida'], axis = 1, inplace = True)

    # Reprocesar nuevas columnas
    df['falta_lunes_viernes'] = df.groupby('empleado_id')['falta_lunes_viernes'].transform(lambda x: (x == 1).sum())
    df['llegada_tarde'] = df.groupby('empleado_id')['llegada_tarde'].transform(lambda x: (x == 1).sum())
    df['retiro_temprano'] = df.groupby('empleado_id')['retiro_temprano'].transform(lambda x: (x == 1).sum())

    return df

def entrenar_isolation_forest(df):
    """Entrena un modelo Isolation Forest para detectar anomalías en la asistencia."""

    # Seleccionar características relevantes
    X = df[['tipo_ausencia', 'faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']]

    # Dividir en entrenamiento y prueba
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

    # Entrenar Isolation Forest
    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(X_train)

    # Evaluar modelo
    y_pred_test = model.predict(X_test)
    y_pred_test = np.where(y_pred_test == -1, 1, 0)
    print("\n* Reporte de clasificación en datos de prueba:")
    print(classification_report(y_pred_test, np.zeros_like(y_pred_test)))

    return model

def resumir_datos_asistencia(df):
    """Genera un resumen de asistencia por empleado y lo guarda en un archivo CSV."""
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

def empleados_asistencia_anomala(df, archivo_destino):
    """Detecta todos los empleados con asistencia anómala y genera un archivo CSV."""

    X = df[['faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']]

    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(X)
    df['anomalia'] = model.predict(X)
    df['anomalia'] = df['anomalia'].apply(lambda x: 1 if x == -1 else 0)

    df_anomalo = df[df['anomalia'] == 1]

    empleados_observados = {
        'empleado_con_muchas_faltas_acumuladas': df_anomalo[df_anomalo['faltas_acumuladas'] > df['faltas_acumuladas'].median()]['empleado_id'].tolist(),
        'empleado_con_faltas_seguidas': df_anomalo[df_anomalo['faltas_seguidas'] > df['faltas_seguidas'].median()]['empleado_id'].tolist(),
        'empleado_falta_lunes_viernes': df_anomalo[df_anomalo['falta_lunes_viernes'] > 0]['empleado_id'].tolist(),
        'empleado_llega_tarde': df_anomalo[df_anomalo['llegada_tarde'] > 0]['empleado_id'].tolist(),
        'empleado_se_retira_antes': df_anomalo[df_anomalo['retiro_temprano'] > 0]['empleado_id'].tolist()
    }

    pd.DataFrame(dict([(k, pd.Series(v)) for k, v in empleados_observados.items()])).to_csv(archivo_destino, index=False)
    print("----> Archivo '{archivo_destino}' generado correctamente.")

def detectar_peores_empleados(df, porcentaje, archivo_destino):
    """Detecta el peor segmento de empleados con asistencia anómala y genera un archivo CSV."""

    # Seleccionar las características relevantes para el análisis
    X = df[['faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']]

    # Entrenar Isolation Forest para detectar anomalías
    model = IsolationForest(contamination = porcentaje / 100, random_state=42)
    model.fit(X)

    # Obtener las puntuaciones de anomalía
    df['anomaly_score'] = model.decision_function(X)

    # Seleccionar los empleados con peor score (más negativos son más anómalos)
    df_peores = df.nsmallest(porcentaje, 'anomaly_score')

    # Guardar el resultado en un nuevo archivo CSV
    df_peores.to_csv(archivo_destino, index=False)

    print("Se ha generado '{archivo_destino}' con los empleados más incumplidores.")
