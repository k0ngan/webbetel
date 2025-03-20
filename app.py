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

def main():
    st.title("Análisis de Recursos Humanos - Implementaciones Actualizadas")
    
    # Subida del archivo de datos (CSV o Excel)
    uploaded_file = st.file_uploader("Seleccione un archivo de datos", type=["csv", "xlsx"])
    
    # Selección del tipo de visualización o análisis
    analysis_type = st.selectbox(
        "Seleccione el tipo de análisis",
        options=["Datos Procesados", "Demográfico", "Contratos", "Salarial", "Asistencia"]
    )
    
    # Filtros opcionales para año y mes
    year = st.text_input("Año (opcional)")
    month = st.text_input("Mes (opcional)")
    
    if uploaded_file is not None:
        # Cargar datos usando la función actualizada que aplica mapeo y normalización
        df = load_hr_data(uploaded_file)
        
        # Filtrar datos por año y/o mes si se han especificado
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
            if analysis_type == "Datos Procesados":
                # Muestra el DataFrame procesado, incluyendo las nuevas columnas normalizadas
                st.write("### Datos Procesados (incluye mapeo y normalización)")
                st.dataframe(df)
            elif analysis_type == "Demográfico":
                fig = demographic_analysis(df)
                st.plotly_chart(fig)
            elif analysis_type == "Contratos":
                fig = contract_analysis(df)
                st.plotly_chart(fig)
            elif analysis_type == "Salarial":
                fig = salary_analysis(df)
                st.plotly_chart(fig)
            elif analysis_type == "Asistencia":
                fig = attendance_analysis(df)
                st.plotly_chart(fig)
                
if __name__ == "__main__":
    main()
