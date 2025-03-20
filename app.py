import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from analisis_hr import load_hr_data, demographic_analysis, contract_analysis, salary_analysis, attendance_analysis

def main():
    st.title("Análisis de Recursos Humanos")
    
    # Subida del archivo
    uploaded_file = st.file_uploader("Seleccione un archivo de datos", type=["csv", "xlsx"])
    
    # Selección del análisis y filtros
    analysis_type = st.selectbox("Seleccione el tipo de análisis", 
                                 options=["demografico", "contratos", "salarial", "asistencia"])
    year = st.text_input("Año (opcional)")
    month = st.text_input("Mes (opcional)")
    
    if uploaded_file is not None:
        # Cargar datos usando la función definida en analisis_hr
        df = load_hr_data(uploaded_file)
        
        # Filtrado según año y/o mes
        if year or month:
            if year and month:
                target_period = f"{year}{month}"
                mask = df['Period'].astype(str).str.strip() == target_period
            elif year:
                mask = df['Period'].astype(str).str.strip().str.startswith(year)
            else:
                mask = df['Period'].astype(str).str.strip().str.endswith(month)
            df = df[mask]
        
        if df.empty:
            st.write("No hay datos para el período seleccionado")
        else:
            # Seleccionar análisis según la opción elegida
            if analysis_type == "demografico":
                fig = demographic_analysis(df)
            elif analysis_type == "contratos":
                fig = contract_analysis(df)
            elif analysis_type == "salarial":
                fig = salary_analysis(df)
            elif analysis_type == "asistencia":
                fig = attendance_analysis(df)
            else:
                fig = None
            
            if fig:
                st.plotly_chart(fig)
                
if __name__ == "__main__":
    main()
