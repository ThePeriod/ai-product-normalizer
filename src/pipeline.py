"""
Pipeline principal para normalización de productos usando Polars y BERT.
Lee archivos CSV de múltiples tiendas, aplica mappings y normaliza datos.
"""
import os
import polars as pl
import json
import logging
from typing import Dict, List
from normalizer import ProductNormalizer

RAW_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")
MAPPINGS_PATH = os.path.join(os.path.dirname(__file__), "mappings.json")


def load_mappings(path: str) -> Dict[str, Dict[str, str]]:
    """Carga el archivo de mappings JSON de columnas por tienda."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def setup_logging():
    """Configura el logging para el pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def process_file(
    fname: str, mapping: Dict[str, str], normalizer: ProductNormalizer
) -> pl.DataFrame:
    """Lee, normaliza y retorna un DataFrame de un archivo CSV dado. Agrega embeddings de descripción."""
    path = os.path.join(RAW_DIR, fname)
    try:
        df = pl.read_csv(path)
        df_norm = normalizer.normalize_dataframe(df, mapping)
        # Agregar columna de embeddings para la descripción
        if "descripcion" in df_norm.columns:
            def embed_desc(desc):
                return normalizer.get_embedding(desc).tolist()
            df_norm = df_norm.with_columns(
                pl.col("descripcion").map_elements(embed_desc, return_dtype=pl.List(pl.Float32)).alias("embedding")
            )
        out_path = os.path.join(PROCESSED_DIR, f"normalized_{fname.replace('.csv', '.parquet')}")
        df_norm.write_parquet(out_path)
        logging.info(f"{fname} normalizado (guardado como Parquet).")
        return df_norm
    except Exception as e:
        logging.error(f"Error procesando {fname}: {e}")
        return None


def main() -> None:
    """
    Pipeline incremental: solo procesa productos nuevos y cachea embeddings y matches previos.
    """
    normalizer = ProductNormalizer()
    mappings = load_mappings(MAPPINGS_PATH)
    all_dfs: List[pl.DataFrame] = []
    processed_files = set()
    all_products_path = os.path.join(PROCESSED_DIR, "all_products_normalized.parquet")
    processed_log_path = os.path.join(PROCESSED_DIR, "processed_files.log")
    # Leer registro de archivos procesados
    if os.path.exists(processed_log_path):
        with open(processed_log_path, "r", encoding="utf-8") as f:
            processed_files = set([line.strip() for line in f if line.strip()])
    # Cargar productos ya procesados (si existen)
    if os.path.exists(all_products_path):
        df_all = pl.read_parquet(all_products_path)
        all_dfs.append(df_all)
    else:
        df_all = None
    nuevos_archivos = []
    for fname in os.listdir(RAW_DIR):
        if fname.endswith(".csv") and fname in mappings:
            if fname in processed_files:
                logging.info(f"{fname} ya fue procesado; se omite para evitar reprocesamiento.")
                continue
            mapping = mappings[fname]
            df_norm = process_file(fname, mapping, normalizer)
            if df_norm is not None:
                # Agregar columna para saber el origen
                df_norm = df_norm.with_columns(pl.lit(fname).alias("source_file"))
                all_dfs.append(df_norm)
                nuevos_archivos.append(fname)
        elif fname.endswith(".csv"):
            logging.warning(f"No hay mapping para {fname}, se omite.")
    if all_dfs:
        df_all_new = pl.concat(all_dfs, how="vertical")
        df_all_new.write_parquet(all_products_path)
        # Actualizar registro de archivos procesados
        if nuevos_archivos:
            with open(processed_log_path, "a", encoding="utf-8") as f:
                for fname in nuevos_archivos:
                    f.write(fname + "\n")
        logging.info("Normalización incremental completada. Archivos guardados en processed (formato Parquet).")
    else:
        logging.warning("No se encontraron archivos CSV para procesar.")



if __name__ == "__main__":
    setup_logging()
    main()
