"""Modelado predictivo (en español)

Modelos: retención (clasificación), frecuencia (regresión) y propensión.
Autor: CMSR92
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    r2_score,
    mean_absolute_error,
)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier

MODELS_DIR = os.path.join("models")


@dataclass
class ClassificationReport:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float


def _split_xy(df: pd.DataFrame, target: str) -> Tuple[pd.DataFrame, pd.Series]:
    X = df.drop(columns=[target])
    y = df[target].astype(int)
    return X, y


def evaluate_classification(y_true, y_pred, y_prob) -> ClassificationReport:
    return ClassificationReport(
        accuracy=accuracy_score(y_true, y_pred),
        precision=precision_score(y_true, y_pred, zero_division=0),
        recall=recall_score(y_true, y_pred, zero_division=0),
        f1=f1_score(y_true, y_pred, zero_division=0),
        roc_auc=roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else float("nan"),
    )


def train_retention_model(df_feat: pd.DataFrame, target: str = "Purchase_Again") -> Tuple[Pipeline, ClassificationReport]:
    """Entrena un modelo de retención con pipeline simple (num scaler + RF)."""
    X, y = _split_xy(df_feat, target)

    # Separación simple (estratificada si posible)
    stratify = y if y.nunique() > 1 else None
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify)

    # Columnas numéricas
    numeric_cols = X_tr.select_dtypes(include=["int64", "float64"]).columns.tolist()
    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric_cols)
    ], remainder="drop")

    clf = RandomForestClassifier(n_estimators=200, random_state=42)

    pipe = Pipeline([
        ("prep", pre),
        ("clf", clf)
    ])

    pipe.fit(X_tr, y_tr)
    y_pred = pipe.predict(X_te)
    y_prob = pipe.predict_proba(X_te)[:, 1]
    report = evaluate_classification(y_te, y_pred, y_prob)
    return pipe, report


def train_frequency_model(df_feat: pd.DataFrame, y_reg: pd.Series) -> Tuple[Pipeline, Dict[str, float]]:
    """Entrena un modelo de frecuencia de visitas (regresión simple)."""
    X = df_feat.copy()
    y = y_reg.astype(float)

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    numeric_cols = X_tr.select_dtypes(include=["int64", "float64"]).columns.tolist()

    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric_cols)
    ], remainder="drop")

    reg = Ridge(alpha=1.0)
    pipe = Pipeline([("prep", pre), ("reg", reg)])
    pipe.fit(X_tr, y_tr)

    y_hat = pipe.predict(X_te)
    metrics = {
        "r2": float(r2_score(y_te, y_hat)),
        "mae": float(mean_absolute_error(y_te, y_hat)),
    }
    return pipe, metrics


def train_propensity_model(df_feat: pd.DataFrame, target: str = "Purchase_Again") -> Tuple[Pipeline, ClassificationReport]:
    """Modelo alternativo simple (Logistic Regression) para propensión."""
    X, y = _split_xy(df_feat, target)
    stratify = y if y.nunique() > 1 else None
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify)

    numeric_cols = X_tr.select_dtypes(include=["int64", "float64"]).columns.tolist()
    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric_cols)
    ], remainder="drop")

    clf = LogisticRegression(max_iter=1000)
    pipe = Pipeline([("prep", pre), ("clf", clf)])
    pipe.fit(X_tr, y_tr)

    y_pred = pipe.predict(X_te)
    y_prob = pipe.predict_proba(X_te)[:, 1]
    report = evaluate_classification(y_te, y_pred, y_prob)
    return pipe, report


def save_model(model: Pipeline, filename: str) -> str:
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, filename)
    joblib.dump(model, path)
    return path


def load_model(filename: str):
    path = os.path.join(MODELS_DIR, filename)
    return joblib.load(path)
