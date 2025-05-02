"""
ProductNormalizer: Clase para normalización y vectorización de productos usando BERT y Polars.
"""
from typing import Dict, Any
import polars as pl
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class ProductNormalizer:
    """
    Normaliza textos y obtiene embeddings para descripciones de productos.
    Utiliza Sentence Transformers y Polars para manipulación eficiente de datos.
    """
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> None:
        """
        Inicializa el normalizador con el modelo de Sentence Transformers especificado.
        """
        #self.model = SentenceTransformer(model_name)
        self.model = SentenceTransformer(os.path.join(os.path.dirname(__file__), "../product_sbert_model"))

    def normalize_text(self, text: Any) -> str:
        """
        Normaliza un texto: minúsculas, strip, elimina espacios extra.
        """
        if not isinstance(text, str):
            text = str(text)
        return " ".join(text.lower().strip().split())

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Obtiene el embedding de Sentence Transformers de la frase.
        """
        return self.model.encode(text)

    def normalize_dataframe(self, df: pl.DataFrame, mapping: Dict[str, str]) -> pl.DataFrame:
        """
        Renombra columnas según mapping y normaliza valores de texto clave.
        Args:
            df: DataFrame de Polars con los datos originales.
            mapping: Diccionario de mapping de columnas origen -> destino.
        Returns:
            DataFrame de Polars con columnas normalizadas.
        """
        df = df.rename(mapping)
        # Normaliza las columnas de texto si existen
        for col in ["producto", "marca", "descripcion"]:
            if col in df.columns:
                df = df.with_columns(
                    pl.col(col).map_elements(self.normalize_text, return_dtype=str).alias(col)
                )
        return df

