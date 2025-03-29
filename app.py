import streamlit as st
import pandas as pd
import time

import ui
import analysis
import utils

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Dashboard de Recursos Humanos",
        page_icon=":bar_chart:",
        layout="wide"
    )

    # Establece el tema de la interfaz y muestra el encabezado
    ui.set_dark_theme()
    ui.main_header()

    # Sidebar para carga de datos y menú de análisis
    st.sidebar.title("Control de Panel")
    st.sidebar.subheader("📂 Carga de Datos")
    uploaded_file = st.sidebar.file_uploader("Sube tu archivo (CSV/Excel)", type=["csv", "xlsx"])
    
    analisis_opcion = st.sidebar.radio(
        "Seleccione el análisis:",
        [
            "📑 Datos Procesados",
            "Horas Extras vs. Sueldos",
            "Faltas vs. Sueldo",
            "Antigüedad",
            "Dotación",
            "Composición de Ausencias",
            "Empleados Activos (Corte)",
            "Empleados Activos vs Inactivos",
            "Faltas por Cargo y Departamento"
        ]
    )

    if uploaded_file is not None:
        # Barra de progreso simulada
        progress_bar = st.progress(0)
        with st.spinner("Procesando archivo..."):
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)

        # Lectura del archivo
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file, sheet_name=0)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            st.stop()

        st.success("¡Archivo cargado y procesado con éxito!")

        # Diccionario para renombrar columnas (ajusta según tus datos)
        rename_map = {
            "Período": "Periodo",
            "Días de Falta": "DiasFalta",
            "Sueldo Bruto Contractual": "SueldoBrutoContractual",
            "Sueldo Bruto (días trabajados)": "SueldoBrutoDiasTrab",
            "Cantidad de Horas Extras Normales": "HrsExt_Normales",
            "Cantidad de Horas Extras al Doble": "HrsExt_Dobles",
            "Cantidad de Horas Extras al 215%": "HrsExt_215",
            "Antigüedad al corte de mes": "AntiguedadMes",
            "Fecha de Término Contrato": "FechaTerminoContrato",
            "Días Trabajados": "DiasTrabajados",
            "Días de Licencia Normales": "DiasLicenciaNormales",
            "Días de Licencia Maternales": "DiasLicenciaMaternales",
            "Días de Vacaciones": "DiasVacaciones",
            "Cargo": "Cargo",
            "Gerencia": "Gerencia",
            "Causal de Término": "Causal de Término"
        }
        df = df.rename(columns=rename_map)

        # Procesa la columna "Periodo" para convertirla a datetime y extraer Año y Mes
        df = utils.process_period_column(df)

        # Mostrar vista previa y columnas para verificar el renombrado y el procesamiento
        with st.expander("Vista previa y columnas"):
            st.dataframe(df.head(10))
            st.write("Columnas actuales:", df.columns.tolist())

        # Llama a la función de análisis según la opción seleccionada
        if analisis_opcion == "📑 Datos Procesados":
            st.subheader("Datos Procesados")
            st.write("Resumen general de los datos:")
            st.write(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")

        elif analisis_opcion == "Horas Extras vs. Sueldos":
            analysis.horas_extras_vs_sueldos(df)

        elif analisis_opcion == "Faltas vs. Sueldo":
            analysis.faltas_vs_sueldo(df)

        elif analisis_opcion == "Antigüedad":
            analysis.antiguedad(df)

        elif analisis_opcion == "Dotación":
            analysis.dotacion(df)

        elif analisis_opcion == "Composición de Ausencias":
            analysis.composicion_ausencias(df)

        elif analisis_opcion == "Empleados Activos (Corte)":
            analysis.empleados_activos(df)

        elif analisis_opcion == "Empleados Activos vs Inactivos":
            analysis.filtrar_empleados_activos_inactivos(df)

        elif analisis_opcion == "Faltas por Cargo y Departamento":
            analysis.faltas_por_cargo_y_departamento(df)
    else:
        st.info("Por favor, sube un archivo para iniciar el análisis.")

if __name__ == "__main__":
    main()
