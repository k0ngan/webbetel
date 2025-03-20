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

# Inyección de CSS personalizado para una UI moderna y profesional
def inject_css():
    st.markdown("""
    <style>
    /* Fondo degradado y fuente elegante */
    .reportview-container {
        background: linear-gradient(135deg, #f9f9f9 0%, #e0e0e0 100%);
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Barra lateral con fondo blanco y borde sutil */
    .sidebar .sidebar-content {
        background: #ffffff;
        border-right: 1px solid #d3d3d3;
        padding: 20px;
    }
    /* Estilos para títulos */
    h1 {
        color: #343a40;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    h3 {
        color: #495057;
        margin-bottom: 1rem;
    }
    /* Estilos para tarjetas de contenido */
    .card {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
    }
    /* Botones */
    .stButton>button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1.5rem;
        font-size: 1rem;
    }
    /* File uploader con estilo */
    .stFileUploader {
        background: #ffffff;
        border: 2px dashed #007bff;
        border-radius: 5px;
        padding: 20px;
    }
    /* Personalización de selectboxes */
    .stSelectbox {
        border-radius: 5px;
        border: 1px solid #ced4da;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    inject_css()

    # Cabecera con logo (reemplaza la URL por el logo de tu empresa)
    st.image("https://via.placeholder.com/1200x200.png?text=Company+Logo", use_column_width=True)
    st.title("Análisis de Recursos Humanos")
    st.markdown("<h3 style='text-align: center; color: #6c757d;'>Análisis Integral de Datos</h3>", unsafe_allow_html=True)
    
    # Barra lateral para configuración y filtros
    st.sidebar.header("Configuración")
    uploaded_file = st.sidebar.file_uploader("Suba su archivo de datos (CSV o Excel)", type=["csv", "xlsx"])
    
    analysis_type = st.sidebar.selectbox(
        "Seleccione el tipo de análisis",
        options=["Datos Procesados", "Demográfico", "Contratos", "Salarial", "Asistencia"]
    )
    
    if uploaded_file is not None:
        # Cargar datos usando la función de análisis
        df = load_hr_data(uploaded_file)
        
        # Si no existe 'Period', se crea a partir de 'ContractStartDate'
        if 'Period' not in df.columns and 'ContractStartDate' in df.columns:
            df['Period'] = df['ContractStartDate'].dt.strftime("%Y%m")
            
        if 'Period' in df.columns:
            df['Period'] = df['Period'].astype(str)
            unique_years = sorted(set([p[:4] for p in df['Period'] if len(p) >= 4]))
            unique_months = sorted(set([p[4:6] for p in df['Period'] if len(p) >= 6]))
            
            st.sidebar.markdown("### Filtros por Período")
            st.sidebar.markdown(f"**Años disponibles ({len(unique_years)}):**")
            st.sidebar.write(unique_years)
            
            selected_year = st.sidebar.selectbox("Seleccione el año", options=["Todos"] + unique_years)
            selected_month = st.sidebar.selectbox("Seleccione el mes", options=["Todos"] + unique_months)
            
            if selected_year != "Todos":
                df = df[df['Period'].str.startswith(selected_year)]
            if selected_month != "Todos":
                df = df[df['Period'].str.endswith(selected_month)]
            
            if df.empty:
                st.error("No hay datos para el período seleccionado")
                return
        else:
            st.sidebar.warning("No se encontró la columna 'Period' para aplicar filtros.")
        
        # Contenedor principal para mostrar resultados en tarjetas (cards)
        if analysis_type == "Datos Procesados":
            st.markdown("<div class='card'><h3>Datos Procesados</h3></div>", unsafe_allow_html=True)
            st.dataframe(df)
        elif analysis_type == "Demográfico":
            st.markdown("<div class='card'><h3>Análisis Demográfico</h3></div>", unsafe_allow_html=True)
            fig = demographic_analysis(df)
            st.plotly_chart(fig, use_container_width=True)
        elif analysis_type == "Contratos":
            st.markdown("<div class='card'><h3>Análisis de Contratos</h3></div>", unsafe_allow_html=True)
            fig = contract_analysis(df)
            st.plotly_chart(fig, use_container_width=True)
        elif analysis_type == "Salarial":
            st.markdown("<div class='card'><h3>Análisis Salarial</h3></div>", unsafe_allow_html=True)
            fig = salary_analysis(df)
            st.plotly_chart(fig, use_container_width=True)
        elif analysis_type == "Asistencia":
            st.markdown("<div class='card'><h3>Análisis de Asistencia</h3></div>", unsafe_allow_html=True)
            fig = attendance_analysis(df)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Por favor, suba un archivo de datos para comenzar el análisis.")

    # Footer
    st.markdown("""
    <hr>
    <p style="text-align: center; color: #6c757d;">© 2025 Su Empresa. Todos los derechos reservados.</p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
