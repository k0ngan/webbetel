import streamlit as st
import pandas as pd
import plotly.express as px
from analisis_hr import (
    load_hr_data, 
    demographic_analysis, 
    contract_analysis, 
    salary_analysis, 
    attendance_analysis,
    analyze_total_LME,
    analyze_grupo_diagnostico_LME,
    analyze_duracion_LME,
    absenteeism_analysis,      # Se importa la función de ausentismo
    absenteeism_comparison     # Se importa la función para comparativa
)

#########################
# Función de Convalidación de Licencias (Nuevo)
#########################
def convalidacion_licencias(df):
    st.markdown("### Convalidación de Licencias")
    st.write("Esta función agrupa los días de licencia acumulados por empleado en un mismo período y calcula el monto a pagar, considerando un mínimo de días según la ley de Chile.")
    # Se solicita mapear las siguientes columnas:
    req = {
        "EmployeeID": "Seleccione la columna que identifica al empleado (p.ej., Rut o Nombre Completo):",
        "BaseSalary": "Seleccione la columna para el Salario Base:",
        "LicenseDays": "Seleccione la columna para los Días de Licencia (por ejemplo, Licencia Común):",
        "Period": "Seleccione la columna que representa el período (YYYYMM):"
    }
    mapping = mapping_dinamico_por_dato(df, req)
    if len(mapping) == len(req):
        df_conv = df.copy()
        # Convertir a numérico los campos necesarios
        df_conv["BaseSalary"] = pd.to_numeric(df_conv[mapping["BaseSalary"]], errors="coerce")
        df_conv["LicenseDays"] = pd.to_numeric(df_conv[mapping["LicenseDays"]], errors="coerce")
        # Asegurarse de tener el campo de período
        if "Period" not in df_conv.columns:
            df_conv["Period"] = df_conv[mapping["Period"]]
        # Agrupar por empleado y período, sumando los días de licencia; se toma el salario base (se asume constante en el grupo)
        grouped = df_conv.groupby([mapping["EmployeeID"], "Period"]).agg({
            "LicenseDays": "sum",
            "BaseSalary": "first"
        }).reset_index()
        # Permitir definir el mínimo de días a pagar según la ley (valor configurable)
        min_days = st.number_input("Ingrese la cantidad mínima de días de licencia a pagar (según la ley de Chile)", min_value=0, value=5)
        # Calcular el valor diario: se asume que el salario es mensual y se divide por 30
        grouped["DailyWage"] = grouped["BaseSalary"] / 30
        # Si la suma de días de licencia es menor al mínimo, se utiliza el mínimo; de lo contrario se paga el total acumulado
        grouped["LicenciaPagadaDias"] = grouped["LicenseDays"].apply(lambda x: max(x, min_days))
        grouped["PagoLicencia"] = grouped["LicenciaPagadaDias"] * grouped["DailyWage"]
        st.markdown("#### Resultados de Convalidación de Licencias")
        st.dataframe(grouped)
        total_payment = grouped["PagoLicencia"].sum()
        st.markdown(f"**Pago Total de Licencias en el período:** ${total_payment:,.2f}")
    else:
        st.info("Complete el mapeo para la convalidación de licencias.")

#########################
# Funciones del Dashboard
#########################
def inject_css():
    st.markdown("""
    <style>
    body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; color: #333; }
    .main-header {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white; padding: 1.5rem; border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem; text-align: center;
    }
    .dashboard-card {
        background-color: white; padding: 1.5rem; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem; transition: transform 0.2s, box-shadow 0.2s;
    }
    .dashboard-card:hover {
        transform: translateY(-5px); box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .section-title {
        color: #28a745; border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5rem; margin-bottom: 1rem; font-weight: 600;
    }
    .sidebar-header {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white; padding: 1rem; border-radius: 5px;
        margin-bottom: 1rem; text-align: center;
    }
    .stButton>button {
        background-color: #28a745; color: white; border: none;
        border-radius: 5px; padding: 0.5rem 1rem; font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #218838; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="main-header">
            <img src="https://betel-website.s3.us-east-2.amazonaws.com/logos.png" width="120">
            <h1>Dashboard de Recursos Humanos</h1>
            <p>Análisis completo para toma de decisiones estratégicas</p>
        </div>
        """, unsafe_allow_html=True)

def setup_sidebar():
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h3>Control de Panel</h3>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("### 📁 Datos")
    with st.sidebar.expander("ℹ️ Cómo usar esta aplicación", expanded=False):
        st.write("""
        1. Suba su archivo CSV o Excel.
        2. Use los filtros para seleccionar el período deseado.
        3. Elija el tipo de análisis que desea visualizar.
        4. Si es necesario, realice el mapeo de columnas para adaptar los datos.
        """)
    uploaded_file = st.sidebar.file_uploader("Suba su archivo de datos", type=["csv", "xlsx"],
                                               help="Formatos soportados: CSV y Excel (.xlsx)")
    return uploaded_file

def setup_period_filters(df):
    st.sidebar.markdown("### ⏱️ Filtros Temporales")
    if 'Período' not in df.columns and 'ContractStartDate' in df.columns:
        df['Período'] = df['ContractStartDate'].dt.strftime("%Y%m")
        st.sidebar.info("Se creó el campo 'Período' a partir de 'ContractStartDate'")
    if 'Período' in df.columns:
        df['Período'] = df['Período'].astype(str)
        unique_years = sorted(set([p[:4] for p in df['Período'] if len(p) >= 6]))
        unique_months = sorted(set([p[4:6] for p in df['Período'] if len(p) >= 6]))
        month_names = {"01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
                       "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
                       "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"}
        month_options = ["Todos"] + [f"{month_names.get(m, m)} ({m})" for m in unique_months]
        col1, col2 = st.sidebar.columns(2)
        with col1:
            selected_year = st.selectbox("Año", options=["Todos"] + unique_years)
        with col2:
            selected_month_display = st.selectbox("Mes", options=month_options)
        selected_month = "Todos" if selected_month_display == "Todos" else selected_month_display.split("(")[1].strip(")")
        filtered_df = df.copy()
        if selected_year != "Todos":
            filtered_df = filtered_df[filtered_df['Período'].str.startswith(selected_year)]
        if selected_month != "Todos":
            filtered_df = filtered_df[filtered_df['Período'].str.endswith(selected_month)]
        st.sidebar.markdown(f"**Registros mostrados:** {len(filtered_df):,}")
        return filtered_df
    else:
        st.sidebar.warning("No se encontró la columna 'Período'.")
        return df

def display_key_metrics(df):
    st.markdown('<h3 class="section-title">📊 Métricas Clave</h3>', unsafe_allow_html=True)
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(df)}</div><div class='metric-label'>Total Empleados</div></div>", unsafe_allow_html=True)
    with metrics_cols[1]:
        active = len(df[df.get('Status', pd.Series()) == 'Active']) if 'Status' in df.columns else "N/A"
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{active}</div><div class='metric-label'>Empleados Activos</div></div>", unsafe_allow_html=True)
    with metrics_cols[2]:
        avg_salary = df['Salary'].mean() if 'Salary' in df.columns else "N/A"
        salary_display = "${:,.2f}".format(avg_salary) if isinstance(avg_salary, (int, float)) else avg_salary
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{salary_display}</div><div class='metric-label'>Salario Promedio</div></div>", unsafe_allow_html=True)
    with metrics_cols[3]:
        departments = df['Department'].nunique() if 'Department' in df.columns else "N/A"
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{departments}</div><div class='metric-label'>Departamentos</div></div>", unsafe_allow_html=True)

def mapping_dinamico_por_dato(df, requeridos):
    mapeo = {}
    st.markdown("### Asignación de Columnas")
    for key, mensaje in requeridos.items():
        opcion = st.selectbox(mensaje, options=["-- Seleccione --"] + list(df.columns), key=key)
        if opcion != "-- Seleccione --":
            mapeo[key] = opcion
    return mapeo

def display_analysis(df):
    analysis_options = {
        "📋 Datos Procesados": "Datos Procesados",
        "👥 Análisis Demográfico": "Demográfico",
        "📑 Análisis de Contratos": "Contratos",
        "💰 Análisis Salarial": "Salarial",
        "⏰ Análisis de Asistencia": "Asistencia",
        "📈 Análisis LME": "LME",
        "📉 Análisis de Ausentismo": "Ausentismo"
    }
    st.sidebar.markdown("### 📈 Tipo de Análisis")
    selected_analysis = st.sidebar.radio("Seleccione qué desea visualizar:", list(analysis_options.keys()))
    analysis_key = analysis_options[selected_analysis]
    st.markdown(f'<h3 class="section-title">{selected_analysis}</h3>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        if analysis_key == "Datos Procesados":
            st.write("Datos procesados y normalizados listos para análisis")
            search_term = st.text_input("🔍 Buscar en los datos:", "")
            displayed_df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)] if search_term else df
            page_size = st.selectbox("Registros por página:", [10, 20, 50, 100])
            total_pages = max(1, len(displayed_df) // page_size + (1 if len(displayed_df) % page_size > 0 else 0))
            page = st.slider("Página:", 1, total_pages, 1)
            st.dataframe(displayed_df.iloc[(page - 1)*page_size : page*page_size], height=400)
            st.download_button("📥 Descargar datos filtrados", 
                               data=displayed_df.to_csv(index=False).encode('utf-8'),
                               file_name='datos_rrhh_filtrados.csv',
                               mime='text/csv')
        
        elif analysis_key == "Demográfico":
            st.write("Análisis Demográfico de Empleados")
            # --- Mostramos las tablas con las distribuciones numéricas ---
            # Ejemplo: Conteo de grupos de edad
            if 'AgeGroup' in df.columns:
                age_dist = df['AgeGroup'].value_counts().sort_index()
                st.markdown("**Distribución por rangos de edad (tabla):**")
                st.dataframe(age_dist)
            
            # Ejemplo: Conteo de género
            if 'Gender' in df.columns:
                gender_dist = df['Gender'].value_counts()
                st.markdown("**Distribución por género (tabla):**")
                st.dataframe(gender_dist)

            # Ejemplo: Conteo de nacionalidad
            if 'Nationality' in df.columns:
                nat_dist = df['Nationality'].value_counts()
                st.markdown("**Distribución por nacionalidad (tabla):**")
                st.dataframe(nat_dist)

            # --- Gráfico original ---
            fig_default = demographic_analysis(df)
            st.plotly_chart(fig_default, use_container_width=True)

            # Mapeo opcional
            if st.checkbox("Mapear columnas para análisis Demográfico"):
                req = {
                    "Edad": "Seleccione la columna para la Edad:",
                    "Género": "Seleccione la columna para el Género:",
                    "Nacionalidad": "Seleccione la columna para la Nacionalidad:",
                    "Antigüedad": "Seleccione la columna para la Antigüedad (en años):"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_demo = df.copy()
                    try:
                        df_demo["AgeGroup"] = pd.cut(pd.to_numeric(df_demo[mapeo["Edad"]], errors="coerce"),
                                                     bins=[18,25,35,45,55,65,100],
                                                     labels=["18-24","25-34","35-44","45-54","55-64","65+"])
                    except Exception as e:
                        st.error("Error en la columna de Edad: " + str(e))
                    df_demo["Gender"] = df_demo[mapeo["Género"]]
                    df_demo["Nationality"] = df_demo[mapeo["Nacionalidad"]]
                    df_demo["TenureYears"] = pd.to_numeric(df_demo[mapeo["Antigüedad"]], errors="coerce")
                    
                    # --- Mostrar tablas con datos mapeados ---
                    st.markdown("**Datos demográficos mapeados (tabla):**")
                    st.dataframe(df_demo[[mapeo["Edad"], mapeo["Género"], mapeo["Nacionalidad"], mapeo["Antigüedad"]]].head(20))

                    # --- Gráfico con datos mapeados ---
                    st.plotly_chart(demographic_analysis(df_demo), use_container_width=True)
                else:
                    st.info("Complete el mapeo para el análisis Demográfico.")
        
        elif analysis_key == "Contratos":
            st.write("Análisis de Contratos")
            # --- Mostramos la distribución de tipos de contrato en tabla ---
            if 'ContractType' in df.columns:
                contract_dist = df['ContractType'].value_counts()
                st.markdown("**Distribución de tipos de contrato (tabla):**")
                st.dataframe(contract_dist)
            if 'Department' in df.columns and 'ContractType' in df.columns:
                contract_dept = pd.crosstab(df['Department'], df['ContractType'])
                st.markdown("**Contratos por departamento (tabla):**")
                st.dataframe(contract_dept)

            # --- Gráfico original ---
            st.plotly_chart(contract_analysis(df), use_container_width=True)

            # Mapeo opcional
            if st.checkbox("Mapear columnas para análisis de Contratos"):
                req = {
                    "ContractType": "Seleccione la columna para el Tipo de Contrato:",
                    "Department": "Seleccione la columna para el Departamento:"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_contrato = df.copy()
                    df_contrato["ContractType"] = df_contrato[mapeo["ContractType"]]
                    df_contrato["Department"] = df_contrato[mapeo["Department"]]

                    # --- Mostrar tabla de datos mapeados ---
                    crosstab_mapped = pd.crosstab(df_contrato["Department"], df_contrato["ContractType"])
                    st.markdown("**Contratos mapeados (tabla):**")
                    st.dataframe(crosstab_mapped)

                    # --- Gráfico con datos mapeados ---
                    st.plotly_chart(contract_analysis(df_contrato), use_container_width=True)
                else:
                    st.info("Complete el mapeo para análisis de Contratos.")
        
        elif analysis_key == "Salarial":
            st.write("Análisis Salarial")
            # --- Tabla con sueldos por departamento y banda ---
            if 'Department' in df.columns and 'BaseSalary' in df.columns:
                df_temp = df.dropna(subset=['Department','BaseSalary']).copy()
                st.markdown("**Muestra de datos salariales (tabla):**")
                st.dataframe(df_temp[['Department','BaseSalary']].head(20))

            # --- Gráfico original ---
            st.plotly_chart(salary_analysis(df), use_container_width=True)

            # Mapeo opcional
            if st.checkbox("Mapear columnas para análisis Salarial"):
                req = {
                    "Department": "Seleccione la columna para el Departamento:",
                    "BaseSalary": "Seleccione la columna para el Salario Base:"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_salarial = df.copy()
                    df_salarial["Department"] = df_salarial[mapeo["Department"]]
                    df_salarial["BaseSalary"] = pd.to_numeric(df_salarial[mapeo["BaseSalary"]], errors="coerce")

                    # --- Mostrar tabla mapeada ---
                    st.markdown("**Datos salariales mapeados (tabla):**")
                    st.dataframe(df_salarial[['Department','BaseSalary']].head(20))

                    # --- Gráfico con datos mapeados ---
                    st.plotly_chart(salary_analysis(df_salarial), use_container_width=True)
                else:
                    st.info("Complete el mapeo para análisis Salarial.")

            # Nueva opción: Convalidación de Licencias
            if st.checkbox("Realizar Convalidación de Licencias", key="convalidar"):
                convalidacion_licencias(df)
        
        elif analysis_key == "Asistencia":
            st.write("Análisis de Asistencia")
            # --- Tabla con la media de días trabajados, ausencias, etc. ---
            try:
                if 'Department' in df.columns and 'DaysWorked' in df.columns and 'AbsenceDays' in df.columns:
                    attendance_dept = df.groupby('Department')[['DaysWorked','AbsenceDays','VacationDays']].mean().reset_index()
                    st.markdown("**Asistencia promedio por departamento (tabla):**")
                    st.dataframe(attendance_dept)
            except:
                pass

            # --- Gráfico original ---
            st.plotly_chart(attendance_analysis(df), use_container_width=True)

            # Mapeo opcional
            if st.checkbox("Mapear columnas para análisis de Asistencia"):
                req = {
                    "DaysWorked": "Seleccione la columna para Días Trabajados:",
                    "AbsenceDays": "Seleccione la columna para Días de Falta:",
                    "VacationDays": "Seleccione la columna para Días de Vacaciones:"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_asistencia = df.copy()
                    for campo in req.keys():
                        df_asistencia[campo] = pd.to_numeric(df_asistencia[mapeo[campo]], errors="coerce")
                    if "Department" not in df_asistencia.columns:
                        st.error("La columna 'Department' es necesaria para agrupar el análisis de asistencia.")
                    else:
                        # --- Tabla mapeada ---
                        df_asistencia_dept = df_asistencia.groupby('Department')[['DaysWorked','AbsenceDays','VacationDays']].mean().reset_index()
                        st.markdown("**Tabla de asistencia (mapeada):**")
                        st.dataframe(df_asistencia_dept)

                        # --- Gráfico ---
                        st.plotly_chart(attendance_analysis(df_asistencia), use_container_width=True)
                else:
                    st.info("Complete el mapeo para análisis de Asistencia.")
        
        elif analysis_key == "LME":
            st.write("Análisis de Licencias Médicas Electrónicas (LME)")
            # Opciones LME reducidas
            lme_options = ["Total LME", "Grupo Diagnóstico", "Duración Promedio"]
            lme_choice = st.selectbox("Seleccione subanálisis LME:", lme_options)
            
            # Selección del método para mapear 'Tipo de Licencia'
            metodo_tipo = st.radio("Método para mapear 'Tipo de Licencia':", 
                                     options=["Directo desde columna", "Transformar columnas (múltiples)"],
                                     key="metodo_tipo")
            if metodo_tipo == "Transformar columnas (múltiples)":
                transform_diag = st.checkbox("Transformar columnas de diagnóstico (formato ancho a largo)", key="transform_diag")
                if transform_diag:
                    diag_cols = st.multiselect("Seleccione las columnas que contienen diagnósticos", options=list(df.columns))
                    if diag_cols:
                        df_lme = df.copy()
                        id_vars = [col for col in df_lme.columns if col not in diag_cols]
                        df_lme = pd.melt(
                            df_lme,
                            id_vars=id_vars,
                            value_vars=diag_cols,
                            var_name="Tipo de Licencia",
                            value_name="Cantidad"
                        )
                        if st.checkbox("Mapear columnas para análisis LME (Transformación)", key="mapeo_lme_transf"):
                            requeridos_lme = {
                                "Grupo Diagnóstico": "Seleccione la columna para el Grupo Diagnóstico:",
                                "DiasAutorizados": "Seleccione la columna para los Días Autorizados:",
                                "Año": "Seleccione la columna para el Año de Emisión:"
                            }
                            mapping_lme = mapping_dinamico_por_dato(df_lme, requeridos_lme)
                            if len(mapping_lme) == len(requeridos_lme):
                                for campo in ["DiasAutorizados"]:
                                    df_lme[campo] = pd.to_numeric(df_lme[mapping_lme[campo]], errors="coerce")
                                for campo in ["Grupo Diagnóstico", "Año"]:
                                    df_lme[campo] = df_lme[mapping_lme[campo]]
                                
                                # Ejecutamos el análisis y mostramos los resultados numéricos + el gráfico
                                if lme_choice == "Total LME":
                                    pivot, fig = analyze_total_LME(df_lme)
                                    st.markdown("**Tabla resumen Total LME**")
                                    st.dataframe(pivot)
                                    st.plotly_chart(fig, use_container_width=True)
                                elif lme_choice == "Grupo Diagnóstico":
                                    pivot, fig = analyze_grupo_diagnostico_LME(df_lme)
                                    st.markdown("**Tabla LME por Grupo Diagnóstico**")
                                    st.dataframe(pivot)
                                    st.plotly_chart(fig, use_container_width=True)
                                elif lme_choice == "Duración Promedio":
                                    duracion, fig = analyze_duracion_LME(df_lme)
                                    st.markdown("**Tabla de Duración Promedio**")
                                    st.dataframe(duracion)
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Seleccione todas las columnas requeridas para el análisis de LME.")
                    else:
                        st.info("Seleccione al menos una columna para transformación de diagnóstico.")
                else:
                    st.info("Active la opción de transformación para mapear 'Tipo de Licencia' desde columnas.")
            else:
                if st.checkbox("Mapear columnas para análisis LME", key="mapeo_lme_directo"):
                    requeridos_lme = {
                        "Tipo de Licencia": "Seleccione la columna para el Tipo de Licencia:",
                        "Cantidad": "Seleccione la columna para la Cantidad:",
                        "Grupo Diagnóstico": "Seleccione la columna para el Grupo Diagnóstico:",
                        "DiasAutorizados": "Seleccione la columna para los Días Autorizados:",
                        "Año": "Seleccione la columna para el Año de Emisión:"
                    }
                    mapping_lme = mapping_dinamico_por_dato(df, requeridos_lme)
                    if len(mapping_lme) == len(requeridos_lme):
                        df_lme = df.copy()
                        for campo in ["Cantidad", "DiasAutorizados"]:
                            df_lme[campo] = pd.to_numeric(df_lme[mapping_lme[campo]], errors="coerce")
                        for campo in ["Tipo de Licencia", "Grupo Diagnóstico", "Año"]:
                            df_lme[campo] = df_lme[mapping_lme[campo]]
                        
                        if lme_choice == "Total LME":
                            pivot, fig = analyze_total_LME(df_lme)
                            st.markdown("**Tabla resumen Total LME**")
                            st.dataframe(pivot)
                            st.plotly_chart(fig, use_container_width=True)
                        elif lme_choice == "Grupo Diagnóstico":
                            pivot, fig = analyze_grupo_diagnostico_LME(df_lme)
                            st.markdown("**Tabla LME por Grupo Diagnóstico**")
                            st.dataframe(pivot)
                            st.plotly_chart(fig, use_container_width=True)
                        elif lme_choice == "Duración Promedio":
                            duracion, fig = analyze_duracion_LME(df_lme)
                            st.markdown("**Tabla de Duración Promedio**")
                            st.dataframe(duracion)
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Seleccione todas las columnas requeridas para el análisis de LME.")
                else:
                    # Sin mapeo, usar datos por defecto
                    if lme_choice == "Total LME":
                        pivot, fig = analyze_total_LME(df)
                        st.markdown("**Tabla resumen Total LME (datos por defecto)**")
                        st.dataframe(pivot)
                        st.plotly_chart(fig, use_container_width=True)
                    elif lme_choice == "Grupo Diagnóstico":
                        pivot, fig = analyze_grupo_diagnostico_LME(df)
                        st.markdown("**Tabla LME por Grupo Diagnóstico (datos por defecto)**")
                        st.dataframe(pivot)
                        st.plotly_chart(fig, use_container_width=True)
                    elif lme_choice == "Duración Promedio":
                        duracion, fig = analyze_duracion_LME(df)
                        st.markdown("**Tabla de Duración Promedio (datos por defecto)**")
                        st.dataframe(duracion)
                        st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_key == "Ausentismo":
            st.write("Análisis de Ausentismo")
            if st.checkbox("Mapear columnas para análisis de Ausentismo"):
                req = {
                    "Fecha": "Seleccione la columna para la Fecha de Ausentismo (opcional):",
                    "AbsenceDays": "Seleccione la columna para los Días de Ausentismo:"
                }
                mapeo = mapping_dinamico_por_dato(df, req)
                if len(mapeo) == len(req):
                    df_abs = df.copy()
                    if mapeo.get("Fecha") and mapeo["Fecha"] != "-- Seleccione --":
                        df_abs['Período'] = pd.to_datetime(df_abs[mapeo["Fecha"]], errors="coerce").dt.strftime("%Y%m")
                    elif 'Período' not in df_abs.columns and 'ContractStartDate' in df_abs.columns:
                        df_abs['Período'] = df_abs['ContractStartDate'].dt.strftime("%Y%m")
                    if mapeo["AbsenceDays"] != "AbsenceDays":
                        df_abs = df_abs.rename(columns={mapeo["AbsenceDays"]: "AbsenceDays"})

                    agg_df, figs, texto_resumen = absenteeism_analysis(df_abs)
                    if agg_df is not None:
                        st.markdown(texto_resumen)
                        
                        # --- Mostrar la tabla de ausentismo ---
                        st.markdown("**Tabla de ausentismo (mapeada):**")
                        st.dataframe(agg_df)

                        # --- Gráficos ---
                        st.plotly_chart(figs[0], use_container_width=True)  # Barras apiladas
                        st.plotly_chart(figs[1], use_container_width=True)  # Línea evolución
                        pie_option = st.selectbox("Seleccione el gráfico de pastel a mostrar:", ["Absoluta", "Porcentual"], key="pie_sel")
                        st.plotly_chart(figs[2][pie_option], use_container_width=True)
                        
                        st.markdown("### Comparativa de Períodos de Ausentismo")
                        available_periods = agg_df['Período'].tolist()
                        col1, col2 = st.columns(2)
                        with col1:
                            period1 = st.selectbox("Seleccione el primer período (YYYYMM):", available_periods, key="comp1")
                        with col2:
                            period2 = st.selectbox("Seleccione el segundo período (YYYYMM):", available_periods, key="comp2")
                        if st.button("Generar Comparativa"):
                            try:
                                comp_df, comp_fig, comp_text = absenteeism_comparison(agg_df, period1, period2)
                                st.markdown("**Tabla comparativa de ausentismo:**")
                                st.dataframe(comp_df)
                                st.plotly_chart(comp_fig, use_container_width=True)
                                st.markdown(comp_text)
                            except Exception as e:
                                st.error(f"Error generando comparativa: {e}")
                    else:
                        st.error("No se encontraron columnas de ausentismo.")
                else:
                    st.info("Complete el mapeo para el análisis de ausentismo.")
            else:
                agg_df, figs, texto_resumen = absenteeism_analysis(df)
                if agg_df is not None:
                    st.markdown(texto_resumen)
                    
                    # --- Mostrar la tabla ---
                    st.markdown("**Tabla de ausentismo (sin mapeo adicional):**")
                    st.dataframe(agg_df)

                    # --- Gráficos ---
                    st.plotly_chart(figs[0], use_container_width=True)  # Barras apiladas
                    st.plotly_chart(figs[1], use_container_width=True)  # Línea evolución
                    pie_option = st.selectbox("Seleccione el gráfico de pastel a mostrar:", ["Absoluta", "Porcentual"], key="pie_sel_std")
                    st.plotly_chart(figs[2][pie_option], use_container_width=True)
                    
                    st.markdown("### Comparativa de Períodos de Ausentismo")
                    available_periods = agg_df['Período'].tolist()
                    col1, col2 = st.columns(2)
                    with col1:
                        period1 = st.selectbox("Seleccione el primer período (YYYYMM):", available_periods, key="comp1_std")
                    with col2:
                        period2 = st.selectbox("Seleccione el segundo período (YYYYMM):", available_periods, key="comp2_std")
                    if st.button("Generar Comparativa", key="comp_btn_std"):
                        try:
                            comp_df, comp_fig, comp_text = absenteeism_comparison(agg_df, period1, period2)
                            st.markdown("**Tabla comparativa de ausentismo:**")
                            st.dataframe(comp_df)
                            st.plotly_chart(comp_fig, use_container_width=True)
                            st.markdown(comp_text)
                        except Exception as e:
                            st.error(f"Error generando comparativa: {e}")
                else:
                    st.error("No se encontraron columnas de ausentismo con los nombres estándar.")

        st.markdown('</div>', unsafe_allow_html=True)
        
        if analysis_key != "Datos Procesados":
            st.markdown('<h4 class="section-title">🔍 Insights Clave</h4>', unsafe_allow_html=True)
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            if analysis_key == "Demográfico":
                st.markdown("""
                - Distribución por género: Evalúe el balance en la organización.
                - Distribución por edad: Observe cómo se agrupa la plantilla.
                - Diversidad cultural: Analice la procedencia de los empleados.
                """)
            elif analysis_key == "Contratos":
                st.markdown("""
                - Tipos de contrato predominantes: Compare la distribución.
                - Departamentos: Relacione el tipo de contrato con el área.
                """)
            elif analysis_key == "Salarial":
                st.markdown("""
                - Comparación salarial: Revise diferencias entre departamentos.
                - Identificación de brechas: Detecte posibles inequidades.
                - **Convalidación de Licencias:** Calcule cuánto se pagará por licencia médica acumulada, aplicando un mínimo de días a pagar.
                """)
            elif analysis_key == "Asistencia":
                st.markdown("""
                - Patrones de asistencia: Identifique áreas con mayor ausentismo.
                - Correlaciones: Analice la relación entre asistencia y otros factores.
                """)
            elif analysis_key == "LME":
                st.markdown("""
                - Evolución de LME: Compare la cantidad total de licencias emitidas por año.
                - Grupo Diagnóstico: Identifique cuáles diagnósticos son más frecuentes.
                - Duración Promedio: Analice la duración promedio de las licencias por grupo diagnóstico.
                """)
            elif analysis_key == "Ausentismo":
                st.markdown("""
                - Evolución mensual: Observe cómo cambian los días de ausentismo a lo largo del tiempo.
                - Tipos de ausencia: Revise qué tipo de ausencia representa mayor porcentaje.
                - Comparativa: Compare datos entre dos períodos y detecte diferencias estadísticas.
                """)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    inject_css()
    display_header()
    uploaded_file = setup_sidebar()
    if uploaded_file:
        try:
            with st.spinner("Procesando datos..."):
                df = load_hr_data(uploaded_file)
                filtered_df = setup_period_filters(df)
                if filtered_df.empty:
                    st.error("No hay datos para el período seleccionado. Ajuste los filtros.")
                    return
                display_key_metrics(filtered_df)
                display_analysis(filtered_df)
        except Exception as e:
            st.error(f"Error al procesar los datos: {str(e)}")
            st.info("Verifique que el archivo tenga el formato correcto y las columnas necesarias.")
    else:
        st.info("Por favor, suba un archivo Excel o CSV para iniciar el análisis.")

if __name__ == "__main__":
    main()
