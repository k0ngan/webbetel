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
    
    if uploaded_file is not None:
        # Cargar datos usando la función actualizada que aplica mapeo y normalización
        df = load_hr_data(uploaded_file)
        
        # Si no existe la columna 'Period', se intenta crear a partir de 'ContractStartDate'
        if 'Period' not in df.columns and 'ContractStartDate' in df.columns:
            df['Period'] = df['ContractStartDate'].dt.strftime("%Y%m")
        
        # Si la columna 'Period' existe, se extraen las opciones para el filtro
        if 'Period' in df.columns:
            df['Period'] = df['Period'].astype(str)
            # Extraer años y meses únicos asumiendo que 'Period' tiene formato 'YYYYMM'
            unique_years = sorted(set([p[:4] for p in df['Period'] if len(p) >= 4]))
            unique_months = sorted(set([p[4:6] for p in df['Period'] if len(p) >= 6]))
            
            selected_year = st.selectbox("Seleccione el año", options=["Todos"] + unique_years)
            selected_month = st.selectbox("Seleccione el mes", options=["Todos"] + unique_months)
            
            # Filtrar el DataFrame según la selección
            if selected_year != "Todos":
                df = df[df['Period'].str.startswith(selected_year)]
            if selected_month != "Todos":
                df = df[df['Period'].str.endswith(selected_month)]
                
            if df.empty:
                st.write("No hay datos para el período seleccionado")
                return
        else:
            st.write("No se encontró la columna 'Period' para aplicar el filtro de año y mes.")
        
        # Selección del tipo de visualización o análisis
        analysis_type = st.selectbox(
            "Seleccione el tipo de análisis",
            options=["Datos Procesados", "Demográfico", "Contratos", "Salarial", "Asistencia"]
        )
        
        if analysis_type == "Datos Procesados":
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
