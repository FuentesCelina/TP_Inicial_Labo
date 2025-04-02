import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, classification_report
from datetime import datetime, timedelta


"""Carga el dataset de asistencia desde un archivo CSV."""
def cargar_datos(archivo="asistencia_empleados.csv"):
    df = pd.read_csv(archivo)

    # Convertir horas a minutos para análisis numérico (donde no hay ausencia)
    df['min_entrada'] = df['hora_entrada'].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if x != "-" else np.nan)
    df['min_salida'] = df['hora_salida'].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if x != "-" else np.nan)

    # Rellenar ausencias con un valor especial (-1)
    df.fillna(-1, inplace=True)

    return df


"""Entrena un modelo Isolation Forest para detectar anomalías en la asistencia."""
def entrenar_isolation_forest(df):

    # Convertir valores no numéricos a categorías para trabajar en isolation_forest
    df['dia_semana'] = df['dia_semana'].astype('category').cat.codes
    df['tipo_ausencia'] = df['tipo_ausencia'].replace({
        "Ninguna": 0,
        "Enfermedad": 1,
        "Falta injustificada": 2,
        "Franco": 3,
        "Alarga fin de semana": 4
        })
    
    # Seleccionar solo las columnas relevantes para el modelo
    X = df[['dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']]

    # Dividir en entrenamiento (80%) y prueba (20%)
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

    # Definir el modelo de Isolation Forest
    model = IsolationForest(contamination=0.05, random_state=42)
 
    # Entrenar el modelo
    #¿ES CORRECTO? X_Train ya quedo con el split lo que se va a entrenar, estas reasignandole a X_train el 100% del dataFrame
    X_train = df[['dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']]

    model.fit(X_train)

    # Evaluar el modelo con los datos de prueba: 1 normal , -1 anómalo
    y_pred_test = model.predict(X_test)

    # Convertir valores (-1 anomalía, 1 normal) a (1 anomalía, 0 normal) para métricas
    y_pred_test = np.where(y_pred_test == -1, 1, 0)
    
    # Imprimir evaluación del modelo
    print("\n* Reporte de clasificación en datos de prueba:")
    print(classification_report(y_pred_test, np.zeros_like(y_pred_test),zero_division=0)) #el zero_division es para los warnings de division de cero

    return model

#Detecta anomalías en el dataset usando el modelo entrenado
def detectar_anomalias(model, df):
    X = df[['dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']]

    # Predecir anomalías
    df['anomalia'] = model.predict(X)

    # Convertir (-1 anomalía, 1 normal) a (1 anomalía, 0 normal)
    df['anomalia'] = df['anomalia'].apply(lambda x: 1 if x == -1 else 0)

    # Filtrar empleados con asistencia anómala
    df_anomalias = df[df['anomalia'] == 1]
    
    print(f"\n🔍 Se encontraron {len(df_anomalias)} registros anómalos.")

    print(f"\n🔍Analisis de inasistencias:")

    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==1])} son de enfermedad")
    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==2])} son de falta injustificada")
    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==3])} son de franco")
    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==4])} son de alargar fin de semana")
    
    print(f"\n🔍Analisis de asistencias:")

    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==0])} son de asistencias")
  
    print(f"\n🔍 {len(df_anomalias[df_anomalias['hora_entrada']=='09:30'])} son de asistencias de entrada tardia")
    print(f"\n🔍 {len(df_anomalias[df_anomalias['hora_salida']=="15:00"])} son de asistencias de salida temprana")
    
    #ESTO PODRIA SER INNECESARIO 
    print(df_anomalias[['empleado_id', 'dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']].head())

    return df_anomalias