# -*- coding: utf-8 -*-
"""
Análisis Integral de Datos de Recursos Humanos con estandarización de columnas y normalización de datos
"""

# =============================================================================
# 1. Importación de librerías
# =============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import unicodedata

# Configuración de visualización
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

# =============================================================================
# 2. Definición de sinónimos para la estandarización de nombres de columnas
# =============================================================================
# Diccionario donde la clave es el nombre estándar y el valor es una lista de posibles sinónimos.
STANDARD_COLUMN_SYNONYMS = {
    'ContractID': ['contrato', 'contractid', 'contract'],
    'NationalID': ['rut', 'nationalid', 'dni'],
    'FullName': ['nombre completo', 'nombre', 'fullname', 'name'],
    'JobRole': ['cargo', 'jobrole', 'position'],
    'Gender': ['sexo', 'gender', 'genero'],
    'BirthDate': ['fecha de nacimiento', 'birthdate', 'nacimiento'],
    'Age': ['edad', 'age'],
    'ContractType': ['tipo de contrato', 'contracttype', 'contract type'],
    'ContractStartDate': ['fecha de inicio contrato', 'start date', 'fecha inicio'],
    'TenureMonths': ['antiguedad al corte de mes', 'tenure', 'antiguedad'],
    'Department': ['gerencia', 'departamento', 'department'],
    'RegularLeaveDays': ['dias de licencia normales', 'regularleavedays', 'licencia normales'],
    'MaternityLeaveDays': ['dias de licencia maternales', 'maternityleavedays', 'licencia maternales'],
    'SickLeaveDays': ['dias con licencia por accidente', 'sickleavedays', 'licencia por accidente'],
    'PermissionDays': ['dias de permiso', 'permissiondays', 'permiso'],
    'AbsenceDays': ['dias de falta', 'absencedays', 'falta'],
    'BaseSalary': ['sueldo bruto contractual', 'basesalary', 'salario']
}

def normalize_string(s):
    """
    Normaliza un string: lo convierte a minúsculas, elimina espacios extremos y remueve acentos.
    """
    if not isinstance(s, str):
        s = str(s)
    s = s.lower().strip()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s

def standardize_column_names(df):
    """
    Revisa cada columna del DataFrame y, si su nombre (normalizado) coincide con alguno
    de los sinónimos definidos, la renombra a la clave estándar.
    """
    new_columns = {}
    for col in df.columns:
        norm_col = normalize_string(col)
        found = False
        for standard, synonyms in STANDARD_COLUMN_SYNONYMS.items():
            synonyms_normalized = [normalize_string(s) for s in synonyms]
            if norm_col in synonyms_normalized:
                new_columns[col] = standard
                found = True
                break
        if not found:
            new_columns[col] = col  # Se mantiene el nombre original si no se encuentra coincidencia.
    return df.rename(columns=new_columns)

# =============================================================================
# 3. Función de mapeo y normalización de columnas numéricas
# =============================================================================
def normalize_and_map_data(df):
    """
    Aplica mapeo de valores y normaliza columnas numéricas específicas.
    
    Mapeo:
      - En la columna 'Gender': 'F' se mapea a 'Femenino' y 'M' a 'Masculino'.
    
    Normalización (min-max) para columnas de asistencia:
      - AbsenceDays, SickLeaveDays, RegularLeaveDays, MaternityLeaveDays, PermissionDays
    """
    # Mapeo de la columna Gender
    gender_mapping = {'F': 'Femenino', 'M': 'Masculino'}
    if 'Gender' in df.columns:
        df['Gender'] = df['Gender'].map(gender_mapping).fillna(df['Gender'])
    
    # Normalización de columnas específicas
    cols_to_normalize = ['AbsenceDays', 'SickLeaveDays', 'RegularLeaveDays', 'MaternityLeaveDays', 'PermissionDays']
    for col in cols_to_normalize:
        if col in df.columns:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val - min_val != 0:
                df[f'Normalized_{col}'] = (df[col] - min_val) / (max_val - min_val)
            else:
                df[f'Normalized_{col}'] = 0.0
    return df

# =============================================================================
# 4. Función de carga y preparación de datos
# =============================================================================
def load_hr_data(file_input):
    """
    Carga datos desde un archivo (CSV o Excel), estandariza los nombres de las columnas,
    convierte las fechas, calcula campos derivados y aplica mapeo y normalización.
    
    Args:
        file_input (file-like object or str): Archivo o ruta.
        
    Returns:
        DataFrame: Datos procesados.
    """
    try:
        # Obtener nombre del archivo (si es un objeto file uploader de Streamlit)
        if hasattr(file_input, 'name'):
            file_name = file_input.name
        else:
            file_name = file_input

        # Cargar datos según el tipo de archivo
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_input, delimiter=';', decimal=',', thousands='.')
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_input)
        else:
            raise ValueError("Formato no soportado")
        
        # Estandarizar los nombres de las columnas usando sinónimos
        df = standardize_column_names(df)
        
        # Si existe la columna 'Faena', convertirla a string para evitar errores de tipo
        if 'Faena' in df.columns:
            df['Faena'] = df['Faena'].fillna('').astype(str)
        
        # Convertir columnas de fecha a datetime (si existen)
        date_cols = ['BirthDate', 'ContractStartDate', 'ContractEndDate']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        
        # Agregar columna 'Nationality' si no existe
        if 'Nationality' not in df.columns:
            df['Nationality'] = 'Desconocida'
        else:
            df['Nationality'] = df['Nationality'].fillna('Desconocida')
        
        # Calcular campo derivado: TenureYears a partir de TenureMonths (si existe)
        if 'TenureMonths' in df.columns:
            df['TenureYears'] = df['TenureMonths'] / 12
        
        # NUEVO: Generar columna Age si no existe, pero sí tenemos BirthDate
        if 'Age' not in df.columns and 'BirthDate' in df.columns:
            today = pd.Timestamp.now()
            df['Age'] = ((today - df['BirthDate']).dt.days // 365).astype(int)
        
        # Crear grupos de edad usando la columna 'Age'
        if 'Age' in df.columns:
            age_bins = [18, 25, 35, 45, 55, 65, 100]
            age_labels = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
            df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False)
        
        # Aplicar mapeo y normalización de columnas numéricas
        df = normalize_and_map_data(df)
        
        return df
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        return None

# =============================================================================
# 5. Funciones de análisis
# =============================================================================
def demographic_analysis(df):
    """
    Análisis demográfico: Edad, Género y Nacionalidad
    
    Args:
        df (DataFrame): Datos de empleados
        
    Returns:
        Figure: Gráficos interactivos
    """
    print("\n=== Análisis Demográfico ===")
    
    # Crear subplots
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{'type': 'bar'}, {'type': 'pie'}],
               [{'type': 'bar'}, {'type': 'bar'}]],
        subplot_titles=(
            'Distribución por Edad',
            'Distribución por Género',
            'Distribución por Nacionalidad',
            'Antigüedad Promedio por Género'
        )
    )
    
    # Gráfico 1: Distribución por edad
    age_dist = df['AgeGroup'].value_counts().sort_index()
    fig.add_trace(
        go.Bar(x=age_dist.index.astype(str), y=age_dist.values, name='Edad'),
        row=1, col=1
    )
    
    # Gráfico 2: Distribución por género
    gender_dist = df['Gender'].value_counts()
    fig.add_trace(
        go.Pie(labels=gender_dist.index, values=gender_dist.values, name='Género'),
        row=1, col=2
    )
    
    # Gráfico 3: Distribución por nacionalidad
    nationality_dist = df['Nationality'].value_counts()
    fig.add_trace(
        go.Bar(x=nationality_dist.index.astype(str), y=nationality_dist.values, name='Nacionalidad'),
        row=2, col=1
    )
    
    # Gráfico 4: Antigüedad por género
    tenure_by_gender = df.groupby('Gender')['TenureYears'].mean()
    fig.add_trace(
        go.Bar(x=tenure_by_gender.index, y=tenure_by_gender.values, name='Antigüedad'),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Análisis Demográfico")
    return fig

# =============================================================================
# 6. Ejecución principal (para pruebas en entorno local)
# =============================================================================
if __name__ == "__main__":
    # Reemplazar 'sample_data.xlsx' por la ruta del archivo Excel a analizar.
    df = load_hr_data('sample_data.xlsx')
    if df is not None:
        analyses = [demographic_analysis, contract_analysis, salary_analysis, attendance_analysis]
        for analysis in analyses:
            try:
                fig = analysis(df)
                fig.show()
            except Exception as e:
                print(f"Error en {analysis.__name__}: {str(e)}")
        # Guardar datos procesados con las nuevas columnas (ej. normalizadas)
        df.to_csv('datos_procesados.csv', index=False)
        print("\nProceso completado. Datos guardados en 'datos_procesados.csv'")
    else:
        print("Error: No se pudo cargar el archivo de datos")
