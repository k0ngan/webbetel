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

# Función para inyectar CSS dinámicamente según el tema seleccionado
def inject_css(theme):
    if theme == "Dark":
        css = """
            <style>
            .reportview-container {
                background: #121212;
                color: #e0e0e0;
                font-family: 'Helvetica Neue', sans-serif;
            }
            .sidebar .sidebar-content {
                background: #1f1f1f;
                border-right: 1px solid #444;
                padding: 20px;
            }
            h1, h3 {
                color: #bb86fc;
            }
            .card {
                background: #1e1e1e;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
                border: 1px solid #333;
            }
            .stButton>button {
                background-color: #bb86fc;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5rem 1.5rem;
                font-size: 1rem;
            }
            .stFileUploader {
                background: #1e1e1e;
                border: 2px dashed #bb86fc;
                border-radius: 5px;
                padding: 20px;
            }
            .stSelectbox {
                border-radius: 5px;
                border: 1px solid #444;
            }
            </style>
        """
    elif theme == "Light":
        css = """
            <style>
            .reportview-container {
                background: #ffffff;
                color: #000000;
                font-family: 'Helvetica Neue', sans-serif;
            }
            .sidebar .sidebar-content {
                background: #ffffff;
                border-right: 1px solid #d3d3d3;
                padding: 20px;
            }
            h1, h3 {
                color: #28a745;
            }
            .card {
                background: #ffffff;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0px 4px 12px rgba(40, 167, 69, 0.1);
                border: 1px solid #d4edda;
            }
            .stButton>button {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5rem 1.5rem;
                font-size: 1rem;
            }
            .stFileUploader {
                background: #ffffff;
                border: 2px dashed #28a745;
                border-radius: 5px;
                padding: 20px;
            }
            .stSelectbox {
                border-radius: 5px;
                border: 1px solid #ced4da;
            }
            </style>
        """
    elif theme == "Blue":
        css = """
            <style>
            .reportview-container {
                background: #e7f0fd;
                color: #0d1a26;
                font-family: 'Helvetica Neue', sans-serif;
            }
            .sidebar .sidebar-content {
                background: #ffffff;
                border-right: 1px solid #b0c4de;
                padding: 20px;
            }
            h1, h3 {
                color: #1E90FF;
            }
            .card {
                background: #ffffff;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0px 4px 12px rgba(30, 144, 255, 0.1);
                border: 1px solid #b0c4de;
            }
            .stButton>button {
                background-color: #1E90FF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5rem 1.5rem;
                font-size: 1rem;
            }
            .stFileUploader {
                background: #ffffff;
                border: 2px dashed #1E90FF;
                border-radius: 5px;
                padding: 20px;
            }
            .stSelectbox {
                border-radius: 5px;
                border: 1px solid #b0c4de;
            }
            </style>
        """
    elif theme == "Green":
        css = """
            <style>
            .reportview-container {
                background: #ffffff;
                color: #000000;
                font-family: 'Helvetica Neue', sans-serif;
            }
            .sidebar .sidebar-content {
                background: #ffffff;
                border-right: 1px solid #d3d3d3;
                padding: 20px;
            }
            h1, h3 {
                color: #28a745;
            }
            .card {
                background: #ffffff;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0px 4px 12px rgba(40, 167, 69, 0.1);
                border: 1px solid #d4edda;
            }
            .stButton>button {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5rem 1.5rem;
                font-size: 1rem;
            }
            .stFileUploader {
                background: #ffffff;
                border: 2px dashed #28a745;
                border-radius: 5px;
                padding: 20px;
            }
            .stSelectbox {
                border-radius: 5px;
                border: 1px solid #ced4da;
            }
            </style>
        """
    else:
        css = ""
    st.markdown(css, unsafe_allow_html=True)

def main():
    # Selección del tema en la barra lateral
    st.sidebar.header("Configuración de Tema")
    theme = st.sidebar.selectbox(
        "Seleccione el estilo de color de la página",
        options=["Light", "Dark", "Blue", "Green"],
        index=0
    )
    inject_css(theme)

    # Cabecera con logo reducido
    st.image("https://betel-website.s3.us-east-2.amazonaws.com/logos.png", width=200)
    st.title("Análisis de Recursos Humanos")
    st.markdown("<h3 style='text-align: center;'>Análisis Integral de Datos</h3>", unsafe_allow_html=True)
    
    # Barra lateral para configuración y filtros adicionales
    st.sidebar.header("Opciones de Configuración")
    uploaded_file = st.sidebar.file_uploader("Suba su archivo de datos (CSV o Excel)", type=["csv", "xlsx"])
    
    analysis_type = st.sidebar.selectbox(
        "Seleccione el tipo de análisis",
        options=["Datos Procesados", "Demográfico", "Contratos", "Salarial", "Asistencia"]
    )
    
    if uploaded_file is not None:
        df = load_hr_data(uploaded_file)
        
        # Si no existe la columna 'Period', se crea a partir de 'ContractStartDate'
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
        
        # Mostrar análisis según la opción seleccionada
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

    st.markdown("""
    <hr>
    <p style="text-align: center;">© 2025 Su Empresa. Todos los derechos reservados.</p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
