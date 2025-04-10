import procesar_datos

def main():
    # Procesar datos
    df_asistencia = procesar_datos.pre_procesar_datos("asistencia_empleados.csv")

    # Generar DataFrame final, con los datos procesados
    df_final = procesar_datos.resumir_datos_asistencia(df_asistencia)

    # Detecta el porcentaje con peor cumplimiento
    df_final= procesar_datos.detectar_peores_empleados(df_final, "empleados_mas_incumplidores.csv")

    #Exportar gráficos de los valores anómalos obtenidos
    procesar_datos.generar_graficos_anomalias("empleados_mas_incumplidores.csv", 'Gráficas', 'Barras', 'Heatmap')
    
  
if __name__ == '__main__':
    main()
