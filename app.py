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

def filter_data_by_period(df):
    """Filtra los datos por año y mes si existe la columna 'Período'."""
    if 'Período' not in df.columns and 'ContractStartDate' in df.columns:
        df['Período'] = df['ContractStartDate'].dt.strftime("%Y%m")
    
    if 'Período' in df.columns:
        df['Período'] = df['Período'].astype(str)
        unique_years = sorted(set(p[:4] for p in df['Período'] if len(p) >= 6))
        unique_months = sorted(set(p[4:6] for p in df['Período'] if len(p) >= 6))
        
        st.sidebar.write("**Filtros por Período**")
        selected_year = st.sidebar.selectbox("Año", options=["Todos"] + unique_years)
        selected_month = st.sidebar.selectbox("Mes", options=["Todos"] + unique_months)
        
        if selected_year != "Todos":
            df = df[df['Período'].str.startswith(selected_year)]
        if selected_month != "Todos":
            df = df[df['Período'].str.endswith(selected_month)]
        
        if df.empty:
            st.error("No hay datos para el período seleccionado.")
            return None
    else:
        st.sidebar.write("No se encontró la columna 'Período' para aplicar el filtro de año y mes.")
    
    return df

def main():
    inject_css()
    
    st.image("https://betel-website.s3.us-east-2.amazonaws.com/logos.png", width=90)
    st.title("Análisis de Recursos Humanos")
    st.write("Seleccione su archivo de datos y el tipo de análisis deseado.")
    
    uploaded_file = st.sidebar.file_uploader("Suba su archivo (CSV o Excel)", type=["csv", "xlsx"])
    analysis_options = {
        "Datos Procesados": lambda df: st.dataframe(df),
        "Demográfico": demographic_analysis,
        "Contratos": contract_analysis,
        "Salarial": salary_analysis,
        "Asistencia": attendance_analysis
    }
    analysis_type = st.sidebar.selectbox("Seleccione el análisis", list(analysis_options.keys()))
    
    if uploaded_file:
        df = load_hr_data(uploaded_file)
        df = filter_data_by_period(df)
        if df is not None:
            result = analysis_options[analysis_type](df)
            if isinstance(result, px.Figure):
                st.plotly_chart(result)
    else:
        st.write("Por favor, suba un archivo de datos para comenzar el análisis.")

if __name__ == "__main__":
    main()
