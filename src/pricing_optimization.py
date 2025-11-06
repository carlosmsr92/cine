"""Optimización de precios y métricas financieras (en español)

Incluye funciones para break-even, ROI y simulación de escenarios.
Autor: CMSR92
"""
from __future__ import annotations
from typing import Dict, List
import math


def break_even(price: float, fixed_costs: float, variable_cost_per_customer: float) -> float:
    """Calcula el punto de equilibrio en número de suscriptores."""
    margin = price - variable_cost_per_customer
    if margin <= 0:
        return math.inf
    return fixed_costs / margin


def roi(net_benefit: float, initial_investment: float) -> float:
    """ROI en %"""
    if initial_investment == 0:
        return float("inf")
    return (net_benefit / initial_investment) * 100.0


def payback_period(investment: float, annual_benefit: float) -> float:
    """Meses necesarios para recuperar la inversión (aprox)."""
    if annual_benefit <= 0:
        return math.inf
    return (investment / annual_benefit) * 12.0


def simulate_pricing_scenarios(
    prices: List[float],
    adoption_by_price: Dict[float, int],
    fixed_costs: float,
    variable_cost_per_customer: float,
) -> List[Dict]:
    """Simula revenue, margen y break-even para cada precio propuesto.

    adoption_by_price: mapa precio → suscriptores estimados
    """
    results = []
    for p in prices:
        subs = adoption_by_price.get(p, 0)
        revenue = p * subs
        variable_total = variable_cost_per_customer * subs
        contrib_margin = revenue - variable_total
        be = break_even(p, fixed_costs, variable_cost_per_customer)
        results.append({
            "price": p,
            "subscribers": subs,
            "revenue": revenue,
            "contribution_margin": contrib_margin,
            "break_even_subs": be,
            "is_profitable": contrib_margin > fixed_costs,
        })
    return results
