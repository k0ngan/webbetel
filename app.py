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
    absenteeism_analysis,
    absenteeism_comparison
)

# Configuración de página y tema
st.set_page_config(
    page_title="Análisis RRHH",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# Sección de chatbot: funciones para manejar la interacción
# ==========================================================
def chatbot_response(query, df):
    """
    Función simulada para generar la respuesta del chatbot.
    Si la consulta contiene la palabra "gráfico", se invoca la función
    display_analysis para mostrar los gráficos.
    """
    if "gráfico" in query.lower():
        st.info("Mostrando gráficos generados:")
        # Se muestran los gráficos de análisis (puedes llamar a la función que prefieras)
        display_analysis(df)
        return "Aquí están los gráficos generados."
    else:
        return f"Esta es una respuesta simulada a: {query}"

def chatbot_interface(df):
    """
    Interfaz del Chatbot:
    - Inicializa variables en st.session_state para el historial de chat y el input.
    - Permite que el usuario ingrese una consulta y la envíe.
    - Agrega al historial la pregunta del usuario y la respuesta generada.
    """
    # Inicialización de variables de estado (se hace solo una vez)
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""
    
    st.header("Chatbot")
    # Campo de entrada para la consulta del usuario
    user_input = st.text_input("Escribe tu pregunta:", key="user_input")
    
    if st.button("Enviar"):
        # Se genera la respuesta del chatbot (aquí se podría integrar una API o modelo real)
        response = chatbot_response(user_input, df)
        # Se añade la pregunta y respuesta al historial
        st.session_state.chat_history.append({"user": user_input, "bot": response})
        # No se reasigna directamente el valor de 'user_input' ya que el widget ya está instanciado
    
    # Se muestra el historial de la conversación
    for chat in st.session_state.chat_history:
        st.markdown(f"**Tú:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")

# ==========================================================
# Resto de funciones para el dashboard (análisis y visualización)
# ==========================================================

def inject_css():
    st.markdown("""
    <style>
    body { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; color: #333; }
    /* Otros estilos personalizados... */
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
    """
    Función que muestra las diferentes secciones de análisis.
    Este código se mantiene sin modificaciones principales.
    """
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
            # Código para mostrar datos procesados y filtros...
            st.write("Datos procesados y normalizados listos para análisis")
            # ... (resto del código original)
        elif analysis_key == "Demográfico":
            st.write("Análisis Demográfico de Empleados")
            fig_default = demographic_analysis(df)
            st.plotly_chart(fig_default, use_container_width=True)
            # ... (resto del código original)
        elif analysis_key == "Contratos":
            st.write("Análisis de Contratos")
            st.plotly_chart(contract_analysis(df), use_container_width=True)
            # ... (resto del código original)
        elif analysis_key == "Salarial":
            st.write("Análisis Salarial")
            st.plotly_chart(salary_analysis(df), use_container_width=True)
            # ... (resto del código original)
        elif analysis_key == "Asistencia":
            st.write("Análisis de Asistencia")
            st.plotly_chart(attendance_analysis(df), use_container_width=True)
            # ... (resto del código original)
        elif analysis_key == "LME":
            st.write("Análisis de Licencias Médicas Electrónicas (LME)")
            # ... (resto del código original)
        elif analysis_key == "Ausentismo":
            st.write("Análisis de Ausentismo")
            # ... (resto del código original)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# Función principal: Selecciona entre análisis o chatbot
# ==========================================================
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

                # Selector para elegir la sección a visualizar
                section = st.sidebar.radio("Selecciona una sección", ["Análisis", "Chatbot"])
                if section == "Análisis":
                    display_key_metrics(filtered_df)
                    display_analysis(filtered_df)
                elif section == "Chatbot":
                    chatbot_interface(filtered_df)
        except Exception as e:
            st.error(f"Error al procesar los datos: {str(e)}")
            st.info("Verifique que el archivo tenga el formato correcto y las columnas necesarias.")
    else:
        st.info("Por favor, suba un archivo Excel o CSV para iniciar el análisis.")

if __name__ == "__main__":
    main()
