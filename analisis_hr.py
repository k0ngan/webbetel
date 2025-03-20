# -*- coding: utf-8 -*-
"""
Análisis Integral de Datos de Recursos Humanos con estandarización de columnas, normalización y funciones de reporte.
Compatible con app.py para dashboard de RRHH
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
import io

# Configuración de visualización
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

# =============================================================================
# 2. Definición de sinónimos para la estandarización de nombres de columnas
# =============================================================================
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
    'ContractEndDate': ['fecha de término contrato', 'end date', 'fin contrato'],
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
    
    # Normalización de columnas de asistencia
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
        # 1. Detectar el nombre del archivo (útil para file_uploader de Streamlit)
        if hasattr(file_input, 'name'):
            file_name = file_input.name
        else:
            file_name = str(file_input)
        
        # 2. Cargar el DataFrame según la extensión
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_input, delimiter=';', decimal=',', thousands='.')
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_input)
        else:
            raise ValueError("Formato no soportado")
        
        # 3. Estandarizar columnas según diccionario de sinónimos
        df = standardize_column_names(df)
        
        # 4. Manejo de columnas especiales
        if 'Faena' in df.columns:
            df['Faena'] = df['Faena'].fillna('').astype(str)
        
        # 5. Convertir columnas de fecha
        date_cols = ['BirthDate', 'ContractStartDate', 'ContractEndDate']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        
        # 6. Calcular TenureYears si TenureMonths existe
        if 'TenureMonths' in df.columns:
            df['TenureYears'] = df['TenureMonths'] / 12
        
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # NUEVO: Generar columna Age si no existe, pero sí tenemos BirthDate
        if 'Age' not in df.columns and 'BirthDate' in df.columns:
            today = pd.Timestamp.now()
            df['Age'] = ((today - df['BirthDate']).dt.days // 365).astype(int)
        
        # NUEVO: Crear columna Nationality por defecto si no existe
        if 'Nationality' not in df.columns:
            df['Nationality'] = 'Desconocida'
        # Si ya existe pero tiene valores nulos, los rellenamos
        else:
            df['Nationality'] = df['Nationality'].fillna('Desconocida')
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        
        # 7. Crear AgeGroup solo si tenemos la columna Age
        if 'Age' in df.columns:
            age_bins = [18, 25, 35, 45, 55, 65, 100]
            age_labels = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
            df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False)
        
        # 8. Aplicar mapeo y normalización (Gender, AbsenceDays, etc.)
        df = normalize_and_map_data(df)
        
        return df
    
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        return None

# =============================================================================
# 5. Funciones de análisis para los diferentes aspectos (ya existentes para app.py)
# =============================================================================
def demographic_analysis(df):
    """
    Análisis demográfico: Distribución de edad, género y otros indicadores.
    Retorna:
        plotly.graph_objects.Figure: Figura para el dashboard.
    """
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
    if 'AgeGroup' in df.columns:
        age_dist = df['AgeGroup'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(x=age_dist.index.astype(str), y=age_dist.values, name='Edad'),
            row=1, col=1
        )
    if 'Gender' in df.columns:
        gender_dist = df['Gender'].value_counts()
        fig.add_trace(
            go.Pie(labels=gender_dist.index, values=gender_dist.values, name='Género'),
            row=1, col=2
        )
    if 'Nationality' in df.columns:
        nat_dist = df['Nationality'].value_counts()
        fig.add_trace(
            go.Bar(x=nat_dist.index.astype(str), y=nat_dist.values, name='Nacionalidad'),
            row=2, col=1
        )
    if 'Gender' in df.columns and 'TenureYears' in df.columns:
        tenure_by_gender = df.groupby('Gender')['TenureYears'].mean()
        fig.add_trace(
            go.Bar(x=tenure_by_gender.index, y=tenure_by_gender.values, name='Antigüedad'),
            row=2, col=2
        )
    fig.update_layout(height=800, showlegend=False, title_text="Análisis Demográfico")
    return fig

def contract_analysis(df):
    """
    Análisis de tipos de contrato y su distribución.
    Retorna:
        plotly.graph_objects.Figure: Figura para el dashboard.
    """
    if 'ContractType' not in df.columns or 'Department' not in df.columns:
        return go.Figure().update_layout(title="Datos insuficientes para análisis de contratos")
    
    contract_dist = df['ContractType'].value_counts()
    contract_dept = pd.crosstab(df['Department'], df['ContractType'])
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'pie'}, {'type': 'bar'}]],
        subplot_titles=('Distribución de Contratos', 'Contratos por Departamento')
    )
    fig.add_trace(
        go.Pie(labels=contract_dist.index, values=contract_dist.values),
        row=1, col=1
    )
    for contract in contract_dept.columns:
        fig.add_trace(
            go.Bar(x=contract_dept.index.astype(str), y=contract_dept[contract], name=contract),
            row=1, col=2
        )
    fig.update_layout(barmode='stack', title_text="Análisis de Contratos")
    return fig

def salary_analysis(df):
    """
    Análisis de distribución salarial.
    Retorna:
        plotly.express.Figure: Gráfico sunburst con distribución salarial por departamento.
    """
    try:
        if 'Department' not in df.columns or 'BaseSalary' not in df.columns:
            raise ValueError("Columnas necesarias no encontradas")
        df_clean = df.dropna(subset=['Department', 'BaseSalary']).copy()
        bins = [0, 500_000, 1_000_000, 1_500_000, 2_000_000, 3_000_000, float('inf')]
        labels = ['<500k', '500k-1M', '1M-1.5M', '1.5M-2M', '2M-3M', '3M+']
        df_clean['SalaryBand'] = pd.cut(df_clean['BaseSalary'], bins=bins, labels=labels, include_lowest=True)
        df_clean = df_clean.dropna(subset=['SalaryBand'])
        if df_clean.empty:
            raise ValueError("No hay datos válidos para generar el gráfico")
        fig = px.sunburst(
            df_clean,
            path=['Department', 'SalaryBand'],
            values='BaseSalary',
            color='BaseSalary',
            color_continuous_scale='RdBu',
            title='Distribución Salarial por Departamento'
        )
        return fig
    except Exception as e:
        print(f"Error en análisis salarial: {str(e)}")
        return px.scatter(title="Error en datos salariales")

def attendance_analysis(df):
    """
    Análisis de asistencia: calcula totales de licencias y agrupa por departamento.
    Retorna:
        plotly.express.Figure: Gráfico de barras con patrones de asistencia.
    """
    try:
        possible_columns = ['RegularLeaveDays', 'MaternityLeaveDays', 'SickLeaveDays', 'PermissionDays']
        existing_columns = [col for col in possible_columns if col in df.columns]
        if existing_columns:
            df['TotalLeave'] = df[existing_columns].sum(axis=1)
        else:
            df['TotalLeave'] = 0
        if 'Department' not in df.columns or 'DaysWorked' not in df.columns or 'AbsenceDays' not in df.columns:
            raise ValueError("Columnas necesarias para análisis de asistencia no encontradas")
        attendance_dept = df.groupby('Department')[['DaysWorked', 'TotalLeave', 'AbsenceDays']].mean()
        fig = px.bar(
            attendance_dept,
            barmode='group',
            title='Patrones de Asistencia por Departamento',
            labels={'value': 'Días', 'variable': 'Tipo'}
        )
        return fig
    except Exception as e:
        print(f"Error en análisis de asistencia: {str(e)}")
        return px.scatter(title="Error en datos de asistencia")

# =============================================================================
# 6. Funciones adicionales para un análisis integral y generación de reportes
# =============================================================================
def generate_hr_overview(df):
    """
    Genera un resumen con indicadores clave de RRHH.
    Retorna:
        dict: Resumen con total de empleados, edad promedio, salario promedio, etc.
    """
    overview = {}
    overview['total_employees'] = len(df)
    if 'Gender' in df.columns:
        gender_dist = df['Gender'].value_counts()
        overview['gender_distribution'] = gender_dist.to_dict()
    if 'TenureYears' in df.columns:
        overview['avg_tenure'] = df['TenureYears'].mean()
    if 'BaseSalary' in df.columns:
        overview['avg_salary'] = df['BaseSalary'].mean()
    if 'Age' in df.columns:
        overview['avg_age'] = df['Age'].mean()
    if 'Department' in df.columns:
        top_depts = df['Department'].value_counts().head(3)
        overview['top_departments'] = top_depts.to_dict()
    if 'ContractType' in df.columns:
        contract_dist = df['ContractType'].value_counts()
        overview['contract_distribution'] = contract_dist.to_dict()
    if 'DaysWorked' in df.columns and 'AbsenceDays' in df.columns:
        total_worked = df['DaysWorked'].sum()
        total_absence = df['AbsenceDays'].sum()
        overview['attendance_ratio'] = total_worked / (total_worked + total_absence)
    return overview

def analyze_hr_data(df):
    """
    Integra los distintos análisis y retorna un diccionario con todos los resultados.
    Retorna:
        dict: Con claves 'overview', 'demographic', 'contracts', 'salary' y 'attendance'.
    """
    results = {}
    results['overview'] = generate_hr_overview(df)
    results['demographic'] = demographic_analysis(df)
    results['contracts'] = contract_analysis(df)
    results['salary'] = salary_analysis(df)
    results['attendance'] = attendance_analysis(df)
    return results

def export_analysis_report(df, results, format='html'):
    """
    Exporta el reporte del análisis a un formato específico (por ejemplo, HTML o JSON).
    Args:
        df (DataFrame): Datos procesados.
        results (dict): Resultados de los análisis.
        format (str): 'html' o 'json'.
    Retorna:
        str: Reporte en el formato solicitado.
    """
    try:
        if format == 'html':
            html_report = io.StringIO()
            html_report.write("<html><head>")
            html_report.write("<title>Análisis de RRHH</title>")
            html_report.write("<style>")
            html_report.write("body {font-family: 'Segoe UI', sans-serif; padding: 20px;}")
            html_report.write(".header {background-color: #28a745; color: white; padding: 20px; text-align: center;}")
            html_report.write(".section {margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px;}")
            html_report.write("</style></head><body>")
            html_report.write("<div class='header'><h1>Informe de RRHH</h1>")
            html_report.write(f"<p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p></div>")
            html_report.write("<div class='section'><h2>Resumen General</h2>")
            overview = results.get('overview', {})
            for key, value in overview.items():
                html_report.write(f"<p><strong>{key.replace('_', ' ').capitalize()}:</strong> {value}</p>")
            html_report.write("</div>")
            # Se pueden agregar las visualizaciones (usando .to_html() de Plotly) si se desea.
            html_report.write("</body></html>")
            return html_report.getvalue()
        elif format == 'json':
            import json
            return json.dumps(results.get('overview', {}))
        else:
            raise ValueError(f"Formato {format} no soportado")
    except Exception as e:
        print(f"Error al exportar informe: {str(e)}")
        return f"Error al generar informe: {str(e)}"

# =============================================================================
# 7. Ejecución principal para pruebas locales
# =============================================================================
if __name__ == "__main__":
    # Reemplazar 'sample_data.xlsx' por la ruta de tu archivo de datos
    df = load_hr_data('sample_data.xlsx')
    if df is not None:
        print("Datos cargados y procesados correctamente.")
        # Ejemplo de análisis integral
        results = analyze_hr_data(df)
        print("\nResumen General:")
        for key, value in results['overview'].items():
            print(f"{key}: {value}")
        # Mostrar gráficos (si se ejecuta en entorno gráfico)
        results['demographic'].show()
        results['contracts'].show()
        results['salary'].show()
        results['attendance'].show()
        # Exportar reporte HTML (puedes usarlo para descarga en app.py)
        reporte_html = export_analysis_report(df, results, format='html')
        with open('reporte_rrhh.html', 'w', encoding='utf-8') as f:
            f.write(reporte_html)
        print("\nReporte generado: 'reporte_rrhh.html'")
    else:
        print("Error: No se pudo cargar el archivo de datos")
