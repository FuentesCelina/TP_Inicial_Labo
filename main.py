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
generador_de_dataset.generar_dataset()

# Al archivo generado, le agrega empleados con asistencia anómala
agrega_anomalias.agregar_anomalias("asistencia_empleados.csv")

# Cargar datos
df_asistencia = deteccion_anomalias.cargar_datos()

# Entrenar el modelo Isolation Forest
modelo = deteccion_anomalias.entrenar_isolation_forest(df_asistencia)

# Detectar anomalías en el dataset
df_anomalos = deteccion_anomalias.detectar_anomalias(modelo, df_asistencia)

# Guardar los resultados
df_anomalos.to_csv("anomalos_detectados.csv", index=False)
print("\n----> Resultados guardados en 'anomalos_detectados.csv'")