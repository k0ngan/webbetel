# -*- coding: utf-8 -*-
"""
Análisis Integral de Datos de Recursos Humanos
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

# Configuración de visualización
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

# =============================================================================
# 2. Mapeo de columnas y configuración
# =============================================================================
COLUMN_MAPPING = {
    'Contrato': 'ContractID',
    'Rut': 'NationalID',
    'Nombre Completo': 'FullName',
    'Cargo': 'JobRole',
    'Clasificación Contrato': 'ContractClassification',
    'Gerencia Presupuesto': 'BudgetUnit',
    'Gerencia': 'Department',
    'Sub Gerencia': 'SubDepartment',
    'Cod. C. Costo': 'CostCenterCode',
    'Centro de Costo': 'CostCenter',
    'Lugar de Pago': 'PaymentLocation',
    'Sección': 'Section',
    'Faena': 'WorkSite',
    'Sexo': 'Gender',
    'Fecha de Nacimiento': 'BirthDate',
    'Edad al corte de mes': 'Age',
    'Tipo de Contrato': 'ContractType',
    'Fecha de Inicio Contrato': 'ContractStartDate',
    'Antigüedad al corte de mes': 'TenureMonths',
    'Causal de Término': 'TerminationReason',
    'Fecha de Término Contrato': 'ContractEndDate',
    'Nación': 'Nationality',
    'Grado del Cargo': 'JobGrade',
    'Período': 'Period',
    'Días Trabajados': 'DaysWorked',
    'Días de Licencia Normales': 'RegularLeaveDays',
    'Días de Licencia Maternales': 'MaternityLeaveDays',
    'Dias con Licencia por accidente': 'SickLeaveDays',
    'Días de Permiso': 'PermissionDays',
    'Días de Falta': 'AbsenceDays',
    'Días de Vacaciones': 'VacationDays',
    'Sueldo Bruto Contractual': 'BaseSalary',
    'Cantidad de Horas Extras Normales': 'OvertimeNormalHours',
    'Cantidad de Horas Extras al Doble': 'OvertimeDoubleHours',
    'Cantidad de Horas Extras al 215%': 'Overtime215Hours',
    'Cantidad de Horas Permiso': 'PermissionHours',
    'Sueldo Bruto (días trabajados)': 'ActualSalary',
    'Horas Extras Normales': 'OvertimeNormalPay',
    'Horas Extras al Doble': 'OvertimeDoublePay',
    'Horas Extras 215%': 'Overtime215Pay',
    'Horas Permiso': 'PermissionHoursPay'
}

# =============================================================================
# 3. Funciones de carga y preparación de datos
# =============================================================================
def load_hr_data(file_path):
    """
    Carga datos desde archivo Excel/CSV y realiza transformaciones iniciales
    
    Args:
        file_path (str): Ruta del archivo de datos
        
    Returns:
        DataFrame: Datos procesados
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, delimiter=';', decimal=',', thousands='.')
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Formato no soportado")
            
        # Renombrar columnas
        df = df.rename(columns=COLUMN_MAPPING)
        
        # Convertir fechas
        date_cols = ['BirthDate', 'ContractStartDate', 'ContractEndDate']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        
        # Calcular campos derivados
        if 'TenureMonths' in df.columns:
            df['TenureYears'] = df['TenureMonths'] / 12  # Convertir meses a años
            
        # Crear grupos de edad
        age_bins = [18, 25, 35, 45, 55, 65, 100]
        age_labels = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False)
        
        return df
    
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        return None

# =============================================================================
# 4. Funciones de análisis
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
        go.Bar(x=age_dist.index, y=age_dist.values, name='Edad'),
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
        go.Bar(x=nationality_dist.index, y=nationality_dist.values, name='Nacionalidad'),
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

def contract_analysis(df):
    """
    Análisis de tipos de contrato y su distribución
    
    Args:
        df (DataFrame): Datos de empleados
        
    Returns:
        Figure: Gráficos interactivos
    """
    print("\n=== Análisis de Contratos ===")
    
    # Preparar datos
    contract_dist = df['ContractType'].value_counts()
    contract_dept = pd.crosstab(df['Department'], df['ContractType'])
    
    # Crear visualizaciones
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
            go.Bar(x=contract_dept.index, y=contract_dept[contract], name=contract),
            row=1, col=2
        )
    
    fig.update_layout(barmode='stack', title_text="Análisis de Contratos")
    return fig
def salary_analysis(df):
    """Análisis de distribución salarial"""
    print("\n=== Análisis Salarial ===")
    
    try:
        # Limpiar datos antes de procesar
        df_clean = df.dropna(subset=['Department', 'BaseSalary'])
        
        # Crear bandas salariales con manejo de outliers
        bins = [0, 500_000, 1_000_000, 1_500_000, 2_000_000, 3_000_000, float('inf')]
        labels = ['<500k', '500k-1M', '1M-1.5M', '1.5M-2M', '2M-3M', '3M+']
        
        # Manejar valores fuera de rango
        df_clean['SalaryBand'] = pd.cut(
            df_clean['BaseSalary'], 
            bins=bins, 
            labels=labels,
            include_lowest=True
        )
        
        # Eliminar filas con bandas no definidas
        df_clean = df_clean.dropna(subset=['SalaryBand'])
        
        # Verificar datos restantes
        if df_clean.empty:
            raise ValueError("No hay datos válidos para generar el gráfico")
        
        # Generar gráfico
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
    Análisis de asistencia con manejo de columnas opcionales
    """
    print("\n=== Análisis de Asistencia ===")
    
    try:
        # Lista de columnas posibles
        possible_columns = [
            'RegularLeaveDays',
            'MaternityLeaveDays',
            'SickLeaveDays',
            'PermissionDays'
        ]
        
        # Filtrar columnas existentes
        existing_columns = [col for col in possible_columns if col in df.columns]
        
        # Calcular días totales de licencia
        if existing_columns:
            df['TotalLeave'] = df[existing_columns].sum(axis=1)
        else:
            df['TotalLeave'] = 0  # Valor por defecto
            
        # Resto del análisis
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
# 5. Ejecución principal
# =============================================================================
if __name__ == "__main__":
    # Cargar datos (reemplazar con tu ruta real)
    # file_path = 'ruta/a/tu/archivo.xlsx'
    # df = load_hr_data(file_path)
    
    # Para pruebas, generar datos de muestra
    df = load_hr_data('sample_data.xlsx')  # Eliminar en producción
    
    if df is not None:
        # Ejecutar análisis
        analyses = [
            demographic_analysis,
            contract_analysis,
            salary_analysis,
            attendance_analysis
        ]
        
        # Generar y mostrar resultados
        for analysis in analyses:
            try:
                fig = analysis(df)
                fig.show()
            except Exception as e:
                print(f"Error en {analysis.__name__}: {str(e)}")
                
        # Guardar datos procesados
        df.to_csv('datos_procesados.csv', index=False)
        print("\nProceso completado. Datos guardados en 'datos_procesados.csv'")
    else:
        print("Error: No se pudo cargar el archivo de datos")