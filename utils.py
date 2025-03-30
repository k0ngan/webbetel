# utils.py
import pandas as pd

def process_period_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte la columna 'Periodo', que viene en formato 'aaaamm' (ejemplo: '202201'),
    a un objeto datetime y crea columnas adicionales 'Año' y 'Mes'.
    """
    if "Periodo" in df.columns:
        # Asegurarse de que el valor sea de tipo string
        df["Periodo"] = df["Periodo"].astype(str)
        # Convertir la columna al formato datetime usando el formato '%Y%m'
        df["Periodo"] = pd.to_datetime(df["Periodo"], format="%Y%m", errors="coerce")
        # Crear nuevas columnas para Año y Mes
        df["Año"] = df["Periodo"].dt.year
        df["Mes"] = df["Periodo"].dt.month
    return df
# utils.py
import pandas as pd

def process_period_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte la columna 'Periodo', que viene en formato 'aaaamm' (ejemplo: '202201'),
    a un objeto datetime y crea columnas adicionales 'Año' y 'Mes'.
    """
    if "Periodo" in df.columns:
        # Asegurarse de que el valor sea de tipo string
        df["Periodo"] = df["Periodo"].astype(str)
        # Convertir la columna al formato datetime usando el formato '%Y%m'
        df["Periodo"] = pd.to_datetime(df["Periodo"], format="%Y%m", errors="coerce")
        # Crear nuevas columnas para Año y Mes
        df["Año"] = df["Periodo"].dt.year
        df["Mes"] = df["Periodo"].dt.month
    return df
