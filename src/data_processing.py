"""Data processing utilities (en español)

Funciones para cargar, validar, limpiar y guardar datos del proyecto.
Autor: CMSR92
"""
from __future__ import annotations
import os
from typing import Tuple
import pandas as pd

RAW_FILE_DEFAULT = os.path.join("data", "raw", "movie_theatre_sales.csv")
PROCESSED_DIR = os.path.join("data", "processed")


def load_data(path: str = RAW_FILE_DEFAULT) -> pd.DataFrame:
    """Carga el dataset desde CSV.

    Args:
        path: Ruta al CSV crudo.
    Returns:
        DataFrame con los datos cargados.
    Raises:
        FileNotFoundError: si el archivo no existe.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No se encontró el archivo en {path}. Coloca el dataset en data/raw/movie_theatre_sales.csv"
        )
    df = pd.read_csv(path)
    return df


essential_columns = [
    "Age",
    "Ticket_Price",
    "Movie_Genre",
    "Seat_Type",
    "Number_of_Person",
    "Purchase_Again",
]


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpieza básica y validaciones mínimas.

    - Normaliza nombres de columnas
    - Elimina duplicados
    - Quita espacios y rellena valores simples
    - Convierte tipos esperados
    """
    df = df.copy()
    # Normaliza columnas
    df.columns = [c.strip() for c in df.columns]

    # Subconjunto mínimo si faltan columnas
    missing = [c for c in essential_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas esenciales: {missing}")

    # Tipos y valores
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce").clip(lower=0)
    df["Ticket_Price"] = pd.to_numeric(df["Ticket_Price"], errors="coerce").clip(lower=0)
    df["Number_of_Person"] = pd.to_numeric(df["Number_of_Person"], errors="coerce").clip(lower=1)

    # Categóricas
    for c in ["Movie_Genre", "Seat_Type"]:
        df[c] = df[c].astype(str).str.strip().str.title()

    # Target binario
    if df["Purchase_Again"].dtype != "int64" and df["Purchase_Again"].dtype != "int32":
        df["Purchase_Again"] = (
            df["Purchase_Again"].astype(str).str.lower().isin(["yes", "1", "true", "y", "si", "sí"]).astype(int)
        )

    # Duplicados y nulos
    df = df.drop_duplicates().reset_index(drop=True)
    df = df.dropna(subset=["Age", "Ticket_Price", "Number_of_Person"])  # hard drop mínimos

    return df


def save_processed(df: pd.DataFrame, filename: str = "cleaned_data.csv") -> str:
    """Guarda DataFrame procesado en data/processed y devuelve la ruta guardada."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(path, index=False)
    return path


def load_and_clean(raw_path: str = RAW_FILE_DEFAULT) -> Tuple[pd.DataFrame, str]:
    """Atajo: carga, limpia y guarda, devolviendo (df_limpio, ruta_archivo)."""
    df = load_data(raw_path)
    df_clean = basic_clean(df)
    saved = save_processed(df_clean, "cleaned_data.csv")
    return df_clean, saved
