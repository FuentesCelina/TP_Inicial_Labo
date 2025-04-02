import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, classification_report


"""Carga el dataset de asistencia desde un archivo CSV."""
def cargar_datos(archivo="asistencia_empleados.csv"):
    df = pd.read_csv(archivo)

#¿LO UTILIZAMOS PARA ALGO? Parece que esta funcion solo tiene como utilidad cargar datos  
#Podriamos utilizar para declarar que no cumplieron las horas de trabajo del dia

    # Convertir horas a minutos para análisis numérico (donde no hay ausencia)
    df['min_entrada'] = df['hora_entrada'].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if x != "-" else np.nan)
    df['min_salida'] = df['hora_salida'].apply(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if x != "-" else np.nan)

    # Rellenar ausencias con un valor especial (-1)
    df.fillna(-1, inplace=True)

    return df


"""Entrena un modelo Isolation Forest para detectar anomalías en la asistencia."""
def entrenar_isolation_forest(df):

    # Convertir valores no numéricos a categorías
    #SI, PERO CUAL ES CUAL? ¿O que dia representa? ¿y 1, 2, 3...? Lo mismo con tipo de ausencia
    """si queremos pasarlo tal cual se encuentra en el dataFrame es 
    #df['dia_semana'] = pd.Categorical(df['dia_semana'], categories=df['dia_semana'].unique(), ordered=True)
    df['dia_semana_cod'] = df['dia_semana'].cat.codes
    Capaz nos sirve mas adelante para dar informacion sobre qué dias mas se falta de la semana o algo asi
    En el caso de las ausencias y justificacion, necesitariamos asignar 0-> ninguna 1-> falta justificada y asi para
    poder decir anomalia de qué tipo es"""
    df['dia_semana'] = df['dia_semana'].astype('category').cat.codes
    df['tipo_ausencia'] = df['tipo_ausencia'].astype('category').cat.codes

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
    #sacar
    
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
    #ESTO SE TIENE QUE REVISAR SEGUN LO DE ARRIBA: Capaz los que nos falta es hacer un analisis del df de anomalias 
    #en donde revisemos linea por linea por qué esta pasando y llevar un contador. Recien ahi vamos a poder decir por 
    #que pasa

    """"
    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==0])} son registros de entradas tarde")
    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==1])} son registros de salidas temprano")
    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==2])} son registros de faltas consecutivas")
    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==3])} son registros de faltas que se dan los dias lunes o viernes ")
    print(f"\n🔍 {len(df_anomalias[df_anomalias['tipo_ausencia']==4])} son registros de ... ")
    """
    #ESTO PODRIA SER INNECESARIO 
    print(df_anomalias[['empleado_id', 'dia_semana', 'asistencia', 'min_entrada', 'min_salida', 'tipo_ausencia']].head())

    return df_anomalias