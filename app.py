import streamlit as st
import pandas as pd
import plotly.express as px
from analisis_hr import (
    load_hr_data, 
    demographic_analysis, 
    contract_analysis, 
    salary_analysis, 
    attendance_analysis
)

# Configuración de página y tema
st.set_page_config(
    page_title="Análisis RRHH",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS para una interfaz moderna y atractiva
def inject_css():
    st.markdown("""
    <style>
    /* Estilos generales */
    body {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
    }
    
    /* Cabecera principal */
    .main-header {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Tarjetas para secciones */
    .dashboard-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Títulos de secciones */
    .section-title {
        color: #28a745;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Personalización de la barra lateral */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #f8f9fa;
    }
    .sidebar-header {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Botones y elementos interactivos */
    .stButton>button {
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #218838;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Selectbox y otros controles */
    .stSelectbox>div>div, .stFileUploader>div {
        background-color: white;
        border-radius: 5px;
        border: 1px solid #e9ecef;
    }
    
    /* Indicadores y métricas */
    .metric-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        flex: 1;
        min-width: 150px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #28a745;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.3rem;
    }
    
    /* Personalización de gráficos */
    .plot-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Tooltips para ayuda */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Animaciones para cargas */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .loading-animation {
        animation: pulse 1.5s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    """Muestra una cabecera atractiva con logo y título"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="main-header">
            <img src="https://betel-website.s3.us-east-2.amazonaws.com/logos.png" width="120">
            <h1>Dashboard de Recursos Humanos</h1>
            <p>Análisis completo de datos de personal para toma de decisiones estratégicas</p>
        </div>
        """, unsafe_allow_html=True)

def setup_sidebar():
    """Configura una barra lateral mejorada con navegación intuitiva"""
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h3>Control de Panel</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sección de carga de archivos con explicación
    st.sidebar.markdown("### 📁 Datos")
    
    with st.sidebar.expander("ℹ️ Cómo usar esta aplicación", expanded=False):
        st.write("""
        1. Suba su archivo CSV o Excel con datos de RRHH
        2. Utilice los filtros para seleccionar el período deseado
        3. Elija el tipo de análisis para visualizar los resultados
        4. Descargue reportes o comparta visualizaciones
        """)
    
    uploaded_file = st.sidebar.file_uploader(
        "Suba su archivo de datos",
        type=["csv", "xlsx"],
        help="Formatos soportados: CSV y Excel (.xlsx)"
    )
    
    return uploaded_file

def setup_period_filters(df):
    """Configura y aplica filtros de período con interfaz mejorada"""
    st.sidebar.markdown("### ⏱️ Filtros Temporales")
    
    if 'Período' not in df.columns and 'ContractStartDate' in df.columns:
        df['Período'] = df['ContractStartDate'].dt.strftime("%Y%m")
        st.sidebar.info("Se creó el campo 'Período' a partir de 'ContractStartDate'")
    
    if 'Período' in df.columns:
        df['Período'] = df['Período'].astype(str)
        unique_years = sorted(set([p[:4] for p in df['Período'] if len(p) >= 6]))
        unique_months = sorted(set([p[4:6] for p in df['Período'] if len(p) >= 6]))
        
        # Diccionario para convertir números de mes a nombres
        month_names = {
            "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
            "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
            "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
        }
        
        # Opciones más amigables para meses
        month_options = ["Todos"] + [f"{month_names.get(m, m)} ({m})" for m in unique_months]
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            selected_year = st.selectbox("Año", options=["Todos"] + unique_years)
        with col2:
            selected_month_display = st.selectbox("Mes", options=month_options)
            
        # Extraer el código de mes del texto mostrado
        selected_month = "Todos"
        if selected_month_display != "Todos":
            selected_month = selected_month_display.split("(")[1].strip(")")
        
        filtered_df = df.copy()
        if selected_year != "Todos":
            filtered_df = filtered_df[filtered_df['Período'].str.startswith(selected_year)]
        if selected_month != "Todos":
            filtered_df = filtered_df[filtered_df['Período'].str.endswith(selected_month)]
        
        # Mostrar conteo de registros después del filtrado
        st.sidebar.markdown(f"**Registros mostrados:** {len(filtered_df):,}")
        
        return filtered_df
    else:
        st.sidebar.warning("No se encontró la columna 'Período' para aplicar filtros temporales.")
        return df

def display_key_metrics(df):
    """Muestra métricas clave como tarjetas informativas"""
    st.markdown('<h3 class="section-title">📊 Métricas Clave</h3>', unsafe_allow_html=True)
    
    metrics_cols = st.columns(4)
    
    with metrics_cols[0]:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Total Empleados</div>
        </div>
        """.format(len(df)), unsafe_allow_html=True)
        
    with metrics_cols[1]:
        active = len(df[df['Status'] == 'Active']) if 'Status' in df.columns else "N/A"
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Empleados Activos</div>
        </div>
        """.format(active), unsafe_allow_html=True)
    
    with metrics_cols[2]:
        avg_salary = df['Salary'].mean() if 'Salary' in df.columns else "N/A"
        salary_display = "${:,.2f}".format(avg_salary) if isinstance(avg_salary, (int, float)) else avg_salary
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Salario Promedio</div>
        </div>
        """.format(salary_display), unsafe_allow_html=True)
        
    with metrics_cols[3]:
        departments = df['Department'].nunique() if 'Department' in df.columns else "N/A"
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Departamentos</div>
        </div>
        """.format(departments), unsafe_allow_html=True)

def display_analysis(analysis_type, df):
    """Muestra el análisis seleccionado con una presentación mejorada"""
    # Selección del análisis con iconos
    analysis_options = {
        "📋 Datos Procesados": "Datos Procesados",
        "👥 Análisis Demográfico": "Demográfico",
        "📑 Análisis de Contratos": "Contratos",
        "💰 Análisis Salarial": "Salarial",
        "⏰ Análisis de Asistencia": "Asistencia"
    }
    
    st.sidebar.markdown("### 📈 Tipo de Análisis")
    selected_analysis = st.sidebar.radio(
        "Seleccione qué desea visualizar:",
        list(analysis_options.keys())
    )
    
    analysis_key = analysis_options[selected_analysis]
    
    # Contenedor para el análisis con estilo mejorado
    st.markdown(f'<h3 class="section-title">{selected_analysis}</h3>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        if analysis_key == "Datos Procesados":
            st.write("Datos procesados y normalizados listos para análisis")
            
            # Agregar opciones de filtrado y búsqueda
            search_term = st.text_input("🔍 Buscar en los datos:", "")
            
            # Filtrar datos si hay término de búsqueda
            if search_term:
                filtered = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                displayed_df = df[filtered]
                st.write(f"Mostrando {len(displayed_df)} de {len(df)} registros")
            else:
                displayed_df = df
            
            # Agregar paginación
            page_size = st.selectbox("Registros por página:", [10, 20, 50, 100])
            total_pages = max(1, len(displayed_df) // page_size + (1 if len(displayed_df) % page_size > 0 else 0))
            page = st.slider("Página:", 1, total_pages, 1)
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(displayed_df))
            
            # Mostrar los datos con la paginación aplicada
            st.dataframe(displayed_df.iloc[start_idx:end_idx], height=400)
            
            # Opciones de descarga
            st.download_button(
                "📥 Descargar datos filtrados",
                data=displayed_df.to_csv(index=False).encode('utf-8'),
                file_name='datos_rrhh_filtrados.csv',
                mime='text/csv'
            )
            
        elif analysis_key == "Demográfico":
            st.write("Distribución demográfica de los empleados")
            with st.spinner("Generando visualización..."):
                fig = demographic_analysis(df)
                st.plotly_chart(fig, use_container_width=True)
                
        elif analysis_key == "Contratos":
            st.write("Análisis de tipos de contratos y duración")
            with st.spinner("Generando visualización..."):
                fig = contract_analysis(df)
                st.plotly_chart(fig, use_container_width=True)
                
        elif analysis_key == "Salarial":
            st.write("Distribución salarial por departamento y categoría")
            with st.spinner("Generando visualización..."):
                fig = salary_analysis(df)
                st.plotly_chart(fig, use_container_width=True)
                
        elif analysis_key == "Asistencia":
            st.write("Patrones de asistencia y ausentismo")
            with st.spinner("Generando visualización..."):
                fig = attendance_analysis(df)
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Añadir sección de insights basados en el análisis actual
        if analysis_key != "Datos Procesados":
            st.markdown('<h4 class="section-title">🔍 Insights Clave</h4>', unsafe_allow_html=True)
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            
            if analysis_key == "Demográfico":
                st.markdown("""
                - **Distribución por género:** Identifique si existe balance de género en su organización
                - **Distribución por edad:** Analice si su fuerza laboral está equilibrada o concentrada en ciertos grupos etarios
                - **Diversidad cultural:** Evalúe la diversidad cultural y de procedencia en su organización
                """)
            elif analysis_key == "Contratos":
                st.markdown("""
                - **Tipos de contrato predominantes:** Identifique la distribución entre contratos temporales y permanentes
                - **Antigüedad promedio:** Analice la retención de empleados por departamento
                - **Renovaciones:** Evalúe patrones de renovación y conversión a contratos permanentes
                """)
            elif analysis_key == "Salarial":
                st.markdown("""
                - **Distribución salarial:** Identifique posibles brechas salariales por género o departamento
                - **Comparativa de mercado:** Compare sus salarios con benchmarks del sector
                - **Tendencias de incremento:** Analice la evolución salarial a lo largo del tiempo
                """)
            elif analysis_key == "Asistencia":
                st.markdown("""
                - **Patrones de ausentismo:** Identifique departamentos con mayores tasas de ausentismo
                - **Tendencias estacionales:** Analice si existen temporadas con mayor ausentismo
                - **Correlaciones:** Busque correlaciones entre ausentismo y otros factores como carga laboral
                """)
                
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    inject_css()
    display_header()
    
    # Configurar barra lateral
    uploaded_file = setup_sidebar()
    
    if uploaded_file:
        try:
            with st.spinner("Procesando datos..."):
                # Cargar datos
                df = load_hr_data(uploaded_file)
                
                # Aplicar filtros de período
                filtered_df = setup_period_filters(df)
                
                if filtered_df.empty:
                    st.error("No hay datos para el período seleccionado. Por favor, ajuste los filtros.")
                    return
                
                # Mostrar métricas clave
                display_key_metrics(filtered_df)
                
                # Mostrar análisis seleccionado
                display_analysis("Datos Procesados", filtered_df)
                
        except Exception as e:
            st.error(f"Error al procesar los datos: {str(e)}")
            st.info("Verifique que el formato del archivo sea correcto y contenga los campos necesarios para el análisis.")
    else:
        # Mostrar pantalla de bienvenida cuando no hay archivo cargado
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("""
        ## 👋 Bienvenido al Dashboard de Análisis de RRHH
        
        Esta herramienta le permite analizar datos de su departamento de Recursos Humanos de forma visual e intuitiva.
        
        **Para comenzar:**
        1. Suba su archivo CSV o Excel utilizando el botón en la barra lateral
        2. El archivo debe contener información sobre sus empleados (demografía, contratos, salarios, asistencia)
        3. Explore diferentes visualizaciones seleccionando el tipo de análisis deseado
        
        **Funcionalidades principales:**
        - Análisis demográfico de su plantilla
        - Distribución de contratos y rotación
        - Análisis salarial por departamentos
        - Patrones de asistencia y ausentismo
        
        ¿Necesita una plantilla de ejemplo? [Descargar plantilla](https://example.com/template.csv)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mostrar capturas de ejemplo
        st.markdown('<h3 class="section-title">✨ Ejemplos de Visualizaciones</h3>', unsafe_allow_html=True)
        example_cols = st.columns(2)
        with example_cols[0]:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.image("https://via.placeholder.com/600x300?text=Ejemplo+Demográfico", use_column_width=True)
            st.markdown("**Análisis Demográfico**")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with example_cols[1]:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.image("https://via.placeholder.com/600x300?text=Ejemplo+Salarial", use_column_width=True)
            st.markdown("**Análisis Salarial**")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
