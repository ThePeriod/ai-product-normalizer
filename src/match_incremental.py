"""
Matching incremental y detección de casos ambiguos para productos nuevos (Active Learning)
"""
import os
import polars as pl
import numpy as np
from typing import List, Tuple
from normalizer import ProductNormalizer

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")
RAW_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")

# Parámetros de ambigüedad
THRESHOLD_AMBIGUO_MIN = 0.75
THRESHOLD_AMBIGUO_MAX = 0.85


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def load_catalogo_existente(exclude_source: str) -> pl.DataFrame:
    """Carga el catálogo existente, excluyendo productos de la nueva tienda."""
    path = os.path.join(PROCESSED_DIR, "all_products_normalized.parquet")
    df = pl.read_parquet(path)
    return df.filter(pl.col("source_file") != exclude_source)


def load_nuevos_productos(source: str) -> pl.DataFrame:
    """Carga los productos nuevos de la tienda a comparar."""
    path = os.path.join(PROCESSED_DIR, f"normalized_{source.replace('.csv','.parquet')}")
    df = pl.read_parquet(path)
    return df


def match_incremental(nueva_tienda: str) -> Tuple[List[dict], List[dict]]:
    """
    Realiza matching incremental y detecta casos ambiguos para revisión humana.
    Retorna dos listas: matches claros y casos ambiguos.
    """
    catalogo = load_catalogo_existente(nueva_tienda)
    nuevos = load_nuevos_productos(nueva_tienda)
    matches = []
    ambiguos = []
    for idx, row in enumerate(nuevos.iter_rows(named=True)):
        emb_nuevo = np.array(row["embedding"])
        mejor_score = -1
        mejor_idx = None
        mejor_row = None
        scores = []
        for idx2, row2 in enumerate(catalogo.iter_rows(named=True)):
            emb_existente = np.array(row2["embedding"])
            score = cosine_similarity(emb_nuevo, emb_existente)
            scores.append((score, row2))
            if score > mejor_score:
                mejor_score = score
                mejor_idx = idx2
                mejor_row = row2
        # Ambigüedad: ¿hay más de un match en el rango ambiguo?
        ambiguos_candidatos = [r for s, r in scores if THRESHOLD_AMBIGUO_MIN <= s <= THRESHOLD_AMBIGUO_MAX]
        if len(ambiguos_candidatos) > 1 or (THRESHOLD_AMBIGUO_MIN <= mejor_score <= THRESHOLD_AMBIGUO_MAX):
            # Caso ambiguo: requiere revisión humana
            ambiguos.append({
                "producto_nuevo": row["producto"],
                "descripcion_nuevo": row["descripcion"],
                "mejor_score": mejor_score,
                "mejor_match": mejor_row["producto"] if mejor_row else None,
                "descripcion_match": mejor_row["descripcion"] if mejor_row else None,
                "scores": sorted([(float(s), r["producto"]) for s, r in scores], reverse=True)
            })
        else:
            # Match claro
            matches.append({
                "producto_nuevo": row["producto"],
                "descripcion_nuevo": row["descripcion"],
                "mejor_score": mejor_score,
                "mejor_match": mejor_row["producto"] if mejor_row else None,
                "descripcion_match": mejor_row["descripcion"] if mejor_row else None
            })
    return matches, ambiguos


def exportar_ambiguos(ambiguos: List[dict], out_path: str):
    """Exporta los casos ambiguos para revisión humana (CSV)."""
    import csv
    keys = ["producto_nuevo", "descripcion_nuevo", "mejor_score", "mejor_match", "descripcion_match"]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in ambiguos:
            writer.writerow({k: row.get(k, "") for k in keys})


def main():
    import logging
    nueva_tienda = "tiendaF.csv"
    matches, ambiguos = match_incremental(nueva_tienda)
    logging.info(f"Matches claros: {len(matches)}")
    logging.info(f"Casos ambiguos: {len(ambiguos)}")
    exportar_ambiguos(ambiguos, os.path.join(PROCESSED_DIR, "casos_ambiguos.csv"))
    logging.info("Casos ambiguos exportados para revisión humana.")

if __name__ == "__main__":
    main()
