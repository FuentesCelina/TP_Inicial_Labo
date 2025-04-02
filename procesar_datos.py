import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def cargar_datos(archivo):
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
    df['llegada_tarde'] = df['min_entrada'].apply(lambda x: 1 if x > 480 and x != -1 else 0)  # Suponiendo 8:00 AM como entrada normal
    df['retiro_temprano'] = df['min_salida'].apply(lambda x: 1 if x < 1020 and x != -1 else 0)  # Suponiendo 5:00 PM como salida normal

    return df

def entrenar_isolation_forest(df):
    """Entrena un modelo Isolation Forest para detectar anomalías en la asistencia."""

    # Seleccionar características relevantes
    X = df[['dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia',
            'faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']]

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

def detectar_anomalias(model, df):
    """Detecta anomalías en el dataset usando el modelo entrenado."""

    X = df[['dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia',
            'faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']]

    # Predecir anomalías
    df['anomalia'] = model.predict(X)
    df['anomalia'] = df['anomalia'].apply(lambda x: 1 if x == -1 else 0)

    # Filtrar registros anómalos
    df_anomalias = df[df['anomalia'] == 1]

    print(f"\n🔍 Se encontraron {len(df_anomalias)} registros anómalos.")
    print(df_anomalias[['empleado_id', 'dia_semana', 'asistencia', 'faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']].head())

    return df_anomalias

def generar_resumen_asistencia(df):
    """Genera un resumen de asistencia por empleado y lo guarda en un archivo CSV."""
    resumen = df.groupby('empleado_id').agg(
        faltas_acumuladas=('faltas_acumuladas', 'max'),
        faltas_seguidas=('faltas_seguidas', 'max'),
        falta_lunes_viernes=('falta_lunes_viernes', 'sum'),
        llegada_tarde=('llegada_tarde', 'sum'),
        retiro_temprano=('retiro_temprano', 'sum')
    ).reset_index()

    resumen.to_csv('resumen_de_asistencia.csv', index=False)
    print("---> Archivo 'resumen_de_asistencia.csv' generado correctamente.")
