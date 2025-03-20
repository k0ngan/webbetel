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

# Inyección de CSS personalizado para modernizar la UI
def inject_css():
    st.markdown("""
    <style>
    /* Estilo general de la aplicación */
    .reportview-container {
        background: #f5f5f5;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Estilo de la barra lateral */
    .sidebar .sidebar-content {
        background: #ffffff;
        padding: 20px;
    }
    /* Títulos */
    h1, h2, h3 {
        color: #333333;
    }
    /* Botones */
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
    }
    /* Estilos para inputs y selectboxes */
    .stSelectbox, .stFileUploader, .stTextInput {
        border-radius: 5px;
        border: 1px solid #cccccc;
        padding: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    inject_css()
    
    st.title("Análisis de Recursos Humanos")
    st.markdown("## Análisis Integral de Datos con una UI Moderna e Intuitiva")
    
    # Barra lateral para configuración y filtros
    st.sidebar.header("Opciones de Configuración")
    uploaded_file = st.sidebar.file_uploader("Seleccione un archivo (CSV o Excel)", type=["csv", "xlsx"])
    
    analysis_type = st.sidebar.selectbox(
        "Seleccione el tipo de análisis",
        options=["Datos Procesados", "Demográfico", "Contratos", "Salarial", "Asistencia"]
    )
    
    if uploaded_file is not None:
        # Cargar datos usando la función de análisis
        df = load_hr_data(uploaded_file)
        
        # Si no existe la columna 'Period', se crea a partir de 'ContractStartDate'
        if 'Period' not in df.columns and 'ContractStartDate' in df.columns:
            df['Period'] = df['ContractStartDate'].dt.strftime("%Y%m")
        
        if 'Period' in df.columns:
            df['Period'] = df['Period'].astype(str)
            # Extraer años y meses únicos suponiendo formato 'YYYYMM'
            unique_years = sorted(set([p[:4] for p in df['Period'] if len(p) >= 4]))
            unique_months = sorted(set([p[4:6] for p in df['Period'] if len(p) >= 6]))
            
            # Mostrar cuántos años se encontraron
            st.sidebar.markdown(f"**El archivo contiene {len(unique_years)} año(s):**")
            st.sidebar.write(unique_years)
            
            # Filtros para seleccionar año y mes
            selected_year = st.sidebar.selectbox("Seleccione el año", options=["Todos"] + unique_years)
            selected_month = st.sidebar.selectbox("Seleccione el mes", options=["Todos"] + unique_months)
            
            # Aplicar filtrado según la selección
            if selected_year != "Todos":
                df = df[df['Period'].str.startswith(selected_year)]
            if selected_month != "Todos":
                df = df[df['Period'].str.endswith(selected_month)]
                
            if df.empty:
                st.error("No hay datos para el período seleccionado")
                return
        else:
            st.sidebar.warning("No se encontró la columna 'Period' para aplicar filtros de año y mes.")
        
        # Mostrar el análisis seleccionado
        st.sidebar.markdown("---")
        if analysis_type == "Datos Procesados":
            st.subheader("Datos Procesados")
            st.dataframe(df)
        elif analysis_type == "Demográfico":
            st.subheader("Análisis Demográfico")
            fig = demographic_analysis(df)
            st.plotly_chart(fig, use_container_width=True)
        elif analysis_type == "Contratos":
            st.subheader("Análisis de Contratos")
            fig = contract_analysis(df)
            st.plotly_chart(fig, use_container_width=True)
        elif analysis_type == "Salarial":
            st.subheader("Análisis Salarial")
            fig = salary_analysis(df)
            st.plotly_chart(fig, use_container_width=True)
        elif analysis_type == "Asistencia":
            st.subheader("Análisis de Asistencia")
            fig = attendance_analysis(df)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Por favor, suba un archivo para iniciar el análisis.")

if __name__ == "__main__":
    main()
