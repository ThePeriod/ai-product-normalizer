"""
Tests para ProductNormalizer usando Polars.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import polars as pl
from normalizer import ProductNormalizer

def test_normalize_text() -> None:
    """Verifica la normalización básica de texto."""
    norm = ProductNormalizer()
    assert norm.normalize_text("  Café MOLIDO  ") == "café molido"
    assert norm.normalize_text("Leche descremada 1L") == "leche descremada 1l"

def test_normalize_dataframe() -> None:
    """Verifica la normalización de un DataFrame de productos."""
    norm = ProductNormalizer()
    df = pl.DataFrame({
        "producto": [" Café 0.5kg "],
        "marca": ["MarcaA"],
        "precio": [120],
        "descripcion": ["Paquete café 500gr"]
    })
    mapping = {"producto": "producto", "marca": "marca", "precio": "precio", "descripcion": "descripcion"}
    df2 = norm.normalize_dataframe(df, mapping)
    assert df2.shape == (1, 4)
    assert df2["producto"][0] == "café 0.5kg"
    assert df2["marca"][0] == "marcaa"
