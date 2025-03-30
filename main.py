#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      jorge
#
# Created:     30/03/2025
# Copyright:   (c) jorge 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()
import generador_de_dataset
import agrega_anomalias
import deteccion_anomalias

# Generar archivo CSV usado como dataset
generador_de_dataset.generar_dataset("asistencia_empleados.csv")

# Al archivo generado, le agrega empleados con asistencia anómala
agrega_anomalias.agregar_anomalias("asistencia_empleados.csv")

# Cargar datos normales
df_asistencia = deteccion_anomalias.cargar_datos("asistencia_empleados.csv")

# Entrenar con el modelo Isolation Forest
modelo = deteccion_anomalias.entrenar_isolation_forest(df_asistencia)

# Cargar datos con anomalías
df_asistencia_anomala = deteccion_anomalias.cargar_datos("asistencia_empleados_anomalo.csv")

# Detectar anomalías en el dataset con anomalías
df_anomalos = deteccion_anomalias.detectar_anomalias(modelo, df_asistencia_anomala)

# Guardar los resultados
df_anomalos.to_csv("anomalos_detectados.csv", index=False)
print("\n----> Resultados guardados en 'anomalos_detectados.csv'")