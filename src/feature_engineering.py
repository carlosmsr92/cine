"""Feature engineering (en español)

Construcción de variables útiles para segmentación y modelos.
Autor: CMSR92
"""
from __future__ import annotations
import os
from typing import Tuple
import pandas as pd

PROCESSED_DIR = os.path.join("data", "processed")


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Crea variables derivadas básicas.

    - gasto_total_est (Ticket_Price * Number_of_Person)
    - gasto_promedio (igual al precio cuando no hay historial)
    - age_group (bins)
    - one-hot para Movie_Genre y Seat_Type
    """
    df = df.copy()

    df["gasto_total_est"] = df["Ticket_Price"].fillna(0) * df["Number_of_Person"].fillna(1)
    df["gasto_promedio"] = df["Ticket_Price"].fillna(df["Ticket_Price"].median())

    # Agrupación de edades
    bins = [0, 17, 24, 39, 59, 120]
    labels = ["<18", "18-24", "25-39", "40-59", "60+"]
    df["age_group"] = pd.cut(df["Age"], bins=bins, labels=labels, include_lowest=True)

    # One-hot
    df = pd.get_dummies(df, columns=["Movie_Genre", "Seat_Type", "age_group"], drop_first=True)

    return df


def save_features(df: pd.DataFrame, filename: str = "model_features.csv") -> str:
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(path, index=False)
    return path


def build_features_pipeline(df_clean: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """Atajo: crea y guarda features."""
    feat = create_features(df_clean)
    saved = save_features(feat)
    return feat, saved
