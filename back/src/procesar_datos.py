import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.decomposition import PCA

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
    # !!! guardo el archivo de resumen de asistencias y borro id_empleado porque no lo tengo en cuenta para el modelo Isolation forest ni la grafica
    resumen=resumen[['empleado_id','faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']]
    return resumen 

def detectar_peores_empleados(df,archivo_destino):
    """Detecta el peor segmento de empleados con asistencia anómala y genera un archivo CSV."""
    ranking=df.copy()     
    #Sacamos mediante el archivo txt lo que nos pidan: qué porcentaje de anomalías y qué tipo de análisis se requiere
    with open("routes/datos.txt","r") as archivo:
        datos=archivo.read().splitlines()
    
    porcentaje=float(datos[0])
    mascara=[int(linea) for linea in datos[1:]] 

    atributos_para_isolation=['faltas_acumuladas', 'faltas_seguidas', 'falta_lunes_viernes', 'llegada_tarde', 'retiro_temprano']

    # Seleccionar columnas basandose en la mascara
    columnas_seleccionadas = [col for col, uso in zip(atributos_para_isolation, mascara) if uso == 1]
    df= df[columnas_seleccionadas]        

    # Entrenar Isolation Forest
    model = IsolationForest(contamination=porcentaje / 100, random_state=42)
    model.fit(df)

    # Obtener las puntuaciones de anomalía. No modifico df
    ranking['anomaly_score'] = model.decision_function(df)

    # Seleccionar los empleados con peor score
    df_peores = ranking.nsmallest(int(len(ranking) * (porcentaje / 100)), 'anomaly_score')

    #Filtrar resultados a mostrar en peores_empleados


    print(f"el porcentaje de isolation sera '{porcentaje} y las columnas a tratar seran '{columnas_seleccionadas}")

    # Guardar en CSV
    df_peores.to_csv(archivo_destino, index=False)

    # Guardamos modelo de Isolation
    joblib.dump(model,'modelo_isolation_forest.pkl')

    print(f"[OK] Se ha generado '{archivo_destino}' con los empleados más incumplidores.")

    return df  # devolvemos también df para graficar



def graficar_anomalias(df, archivo):
    """Grafica las anomalías detectadas con Isolation Forest"""
    modeloEntrenado=joblib.load(archivo)
    y_pred = modeloEntrenado.predict(df)

    # PCA para reducción a 2 dimensiones (matriz de coordenadas)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(df)

    # Gráfico
    plt.figure(figsize=(15, 8))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y_pred, cmap='coolwarm', edgecolors='k')
    plt.title("Detección de Anomalías con Isolation Forest + PCA")
    plt.xlabel("PC1") #la verdad no lo pondria, no le aclara nada al cliente verlo, se consiguieron las coordenadas con calculos de combinatoria
    plt.ylabel("PC2") #same
    plt.grid(True)
    plt.savefig("deteccion_de_anomalias.png", dpi=300)
    #plt.show() esto es para mostrar, pero nos conviene tenerlo como imagen para poder mostrarlo en la web