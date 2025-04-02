def main():

    import generador_de_dataset
    import agrega_anomalias
    import procesar_datos

    # Generar archivo CSV usado como dataset
    generador_de_dataset.generar_dataset("asistencia_empleados.csv")

    # Al archivo generado, le agrega empleados con asistencia anómala
    agrega_anomalias.agregar_anomalias("asistencia_empleados.csv")

    # Procesar datos
    df_asistencia = procesar_datos.pre_procesar_datos("asistencia_empleados.csv")

    # Entrenar el modelo Isolation Forest
    modelo = procesar_datos.entrenar_isolation_forest(df_asistencia)

    # Generar DataFrame final, sólo con los datos relevantes
    df_final = procesar_datos.resumir_datos_asistencia(df_asistencia)

    # Genera reporte de asistencias anómalas
    procesar_datos.empleados_asistencia_anomala(df_final, "anomalias_de_asistencia.csv")

    # Detecta el porcentaje con peor cumplimiento
    procesar_datos.detectar_peores_empleados(df_final, 20, "empleados_mas_incumplidores.csv")

if __name__ == '__main__':
    main()
