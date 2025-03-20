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

# Inyección de CSS para una UI simple y limpia
def inject_css():
    st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    h1 {
        color: #28a745;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        padding: 20px;
    }
    .card {
        background-color: #ffffff;
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    inject_css()
    
    # Logo pequeño y título
    st.image("https://betel-website.s3.us-east-2.amazonaws.com/logos.png", width=150)
    st.title("Análisis de Recursos Humanos")
    st.write("Seleccione su archivo de datos y el tipo de análisis deseado.")
    
    # Configuración en la barra lateral
    uploaded_file = st.sidebar.file_uploader("Suba su archivo (CSV o Excel)", type=["csv", "xlsx"])
    analysis_type = st.sidebar.selectbox("Seleccione el análisis", 
                                          ["Datos Procesados", "Demográfico", "Contratos", "Salarial", "Asistencia"])
    
    if uploaded_file:
        # Cargar y preparar los datos
        df = load_hr_data(uploaded_file)
        
        # Se asume que la columna "Period" tiene valores en formato "aaaamm" (ej. "202201")
        if 'Period' not in df.columns and 'ContractStartDate' in df.columns:
            df['Period'] = df['ContractStartDate'].dt.strftime("%Y%m")
        
        if 'Period' in df.columns:
            df['Period'] = df['Period'].astype(str)
            unique_years = sorted(set([p[:4] for p in df['Period'] if len(p) >= 6]))
            unique_months = sorted(set([p[4:6] for p in df['Period'] if len(p) >= 6]))
            
            st.sidebar.write("**Filtros por Período**")
            selected_year = st.sidebar.selectbox("Año", options=["Todos"] + unique_years)
            selected_month = st.sidebar.selectbox("Mes", options=["Todos"] + unique_months)
            
            if selected_year != "Todos":
                df = df[df['Period'].str.startswith(selected_year)]
            if selected_month != "Todos":
                df = df[df['Period'].str.endswith(selected_month)]
            
            if df.empty:
                st.error("No hay datos para el período seleccionado.")
                return
        
        # Mostrar el análisis seleccionado
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
        st.info("Por favor, suba un archivo para comenzar.")

if __name__ == "__main__":
    main()
