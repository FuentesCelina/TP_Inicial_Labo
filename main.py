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

    # Generar DataFrame final, con los datos procesados
    df_final = procesar_datos.resumir_datos_asistencia(df_asistencia)

    # Detecta el porcentaje con peor cumplimiento
    procesar_datos.detectar_peores_empleados(df_final, 20, "empleados_mas_incumplidores.csv")

    #Graficar valores normales y anómalos obtenidos
    procesar_datos.graficar_anomalias(df_final,'modelo_isolation_forest.pkl')
    
if __name__ == '__main__':
    main()
