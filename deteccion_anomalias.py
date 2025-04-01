import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def cargar_datos(archivo="asistencia_empleados.csv"):
    """Carga el dataset de asistencia desde un archivo CSV."""
    df = pd.read_csv(archivo)

    # Convertir horas a minutos para análisis numérico (donde no hay ausencia)
    df['min_entrada'] = df['hora_entrada'].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if x != "-" else np.nan)
    df['min_salida'] = df['hora_salida'].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if x != "-" else np.nan)

    # Rellenar ausencias con un valor especial (-1)
    df.fillna(-1, inplace=True)

    return df

def entrenar_isolation_forest(df):
    # """Entrena un modelo Isolation Forest para detectar anomalías en la asistencia."""

    # Convertir valores no numéricos a cetegorías ***** BUG CORREGIDO
    df['dia_semana'] = df['dia_semana'].astype('category').cat.codes
    df['tipo_ausencia'] = df['tipo_ausencia'].astype('category').cat.codes

    # Seleccionar solo las columnas relevantes para el modelo
    X = df[['dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']]

    # Dividir en entrenamiento (80%) y prueba (20%)
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

    # Definir el modelo de Isolation Forest
    model = IsolationForest(contamination=0.05, random_state=42)

    # Entrenar el modelo
    X_train = df[['dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']]

    model.fit(X_train)

    # Evaluar el modelo con los datos de prueba
    y_pred_test = model.predict(X_test)

    # Convertir valores (-1 anomalía, 1 normal) a (1 anomalía, 0 normal) para métricas
    y_pred_test = np.where(y_pred_test == -1, 1, 0)

    # Imprimir evaluación del modelo
    print("\n* Reporte de clasificación en datos de prueba:")
    print(classification_report(y_pred_test, np.zeros_like(y_pred_test)))  # Asumimos que no hay anomalías etiquetadas

    return model

def detectar_anomalias(model, df):
    """Detecta anomalías en el dataset usando el modelo entrenado."""
    X = df[['dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']]

    # Predecir anomalías
    df['anomalia'] = model.predict(X)

    # Convertir (-1 anomalía, 1 normal) a (1 anomalía, 0 normal)
    df['anomalia'] = df['anomalia'].apply(lambda x: 1 if x == -1 else 0)

    # Filtrar empleados con asistencia anómala
    df_anomalias = df[df['anomalia'] == 1]

    print(f"\n🔍 Se encontraron {len(df_anomalias)} registros anómalos.")
    print(df_anomalias[['empleado_id', 'dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']].head())

    return df_anomalias