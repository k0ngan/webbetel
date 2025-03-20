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

# Inyección de CSS para una interfaz simple y limpia
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

def setup_period_filters(df):
    """Configura y aplica filtros de período si están disponibles en el dataframe"""
    if 'Período' not in df.columns and 'ContractStartDate' in df.columns:
        df['Período'] = df['ContractStartDate'].dt.strftime("%Y%m")
    
    if 'Período' in df.columns:
        df['Período'] = df['Período'].astype(str)
        unique_years = sorted(set([p[:4] for p in df['Período'] if len(p) >= 6]))
        unique_months = sorted(set([p[4:6] for p in df['Período'] if len(p) >= 6]))
        
        st.sidebar.write("**Filtros por Período**")
        selected_year = st.sidebar.selectbox("Año", options=["Todos"] + unique_years)
        selected_month = st.sidebar.selectbox("Mes", options=["Todos"] + unique_months)
        
        filtered_df = df.copy()
        if selected_year != "Todos":
            filtered_df = filtered_df[filtered_df['Período'].str.startswith(selected_year)]
        if selected_month != "Todos":
            filtered_df = filtered_df[filtered_df['Período'].str.endswith(selected_month)]
        
        return filtered_df
    else:
        st.sidebar.write("No se encontró la columna 'Período' para aplicar filtros temporales.")
        return df

def main():
    inject_css()
    
    # Logo pequeño y título
    st.image("https://betel-website.s3.us-east-2.amazonaws.com/logos.png", width=150)
    st.title("Análisis de Recursos Humanos")
    st.write("Seleccione su archivo de datos y el tipo de análisis deseado.")
    
    # Configuración en la barra lateral
    uploaded_file = st.sidebar.file_uploader("Suba su archivo (CSV o Excel)", type=["csv", "xlsx"])
    
    if uploaded_file:
        # Cargar datos
        df = load_hr_data(uploaded_file)
        
        # Aplicar filtros de período
        filtered_df = setup_period_filters(df)
        
        if filtered_df.empty:
            st.error("No hay datos para el período seleccionado.")
            return
            
        # Selección del tipo de análisis (ahora aparece una sola vez)
        analysis_type = st.sidebar.selectbox(
            "Seleccione el análisis", 
            ["Datos Procesados", "Demográfico", "Contratos", "Salarial", "Asistencia"]
        )
        
        # Mostrar resultados según el análisis seleccionado
        if analysis_type == "Datos Procesados":
            st.write("### Datos Procesados (incluye mapeo y normalización)")
            st.dataframe(filtered_df)
        elif analysis_type == "Demográfico":
            fig = demographic_analysis(filtered_df)
            st.plotly_chart(fig)
        elif analysis_type == "Contratos":
            fig = contract_analysis(filtered_df)
            st.plotly_chart(fig)
        elif analysis_type == "Salarial":
            fig = salary_analysis(filtered_df)
            st.plotly_chart(fig)
        elif analysis_type == "Asistencia":
            fig = attendance_analysis(filtered_df)
            st.plotly_chart(fig)
    else:
        st.write("Por favor, suba un archivo de datos para comenzar el análisis.")

if __name__ == "__main__":
    main()
