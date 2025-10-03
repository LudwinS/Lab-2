import pandas as pd

def cargar_csv(ruta):
    """Carga un CSV y devuelve un DataFrame"""
    df = pd.read_csv(ruta)
    return df

def obtener_resumen(df):
    """Devuelve el resumen estadístico del DataFrame"""
    return df.describe(include="all").fillna("").round(2)

def obtener_tipos(df):
    """Devuelve los tipos de cada columna"""
    return pd.DataFrame(df.dtypes, columns=["Tipo de Dato"])

def obtener_mediciones(df, columna):
    """Calcula media, mediana y desviación estándar de una columna numérica"""
    if columna not in df.columns:
        return None
    media = df[columna].mean()
    mediana = df[columna].median()
    std = df[columna].std()
    return media, mediana, std

def obtener_columnas_numericas(df):
    """Devuelve una lista con las columnas numéricas del DataFrame"""
    return df.select_dtypes(include=["int64", "float64"]).columns.tolist()
