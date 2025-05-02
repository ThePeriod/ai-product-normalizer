import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from normalizer import ProductNormalizer

def cosine_similarity(a, b):
    """Calcula la similitud de coseno entre dos vectores numpy."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def test_embedding_dimensions():
    norm = ProductNormalizer()
    emb = norm.get_embedding("Café molido 500g")
    assert isinstance(emb, np.ndarray)
    assert emb.ndim == 1
    assert emb.shape[0] in (384, 768)  # Modelos SBERT suelen ser 384 o 768

def test_embedding_similarity_identical():
    norm = ProductNormalizer()
    emb1 = norm.get_embedding("Leche descremada 1L")
    emb2 = norm.get_embedding("Leche descremada 1L")
    sim = cosine_similarity(emb1, emb2)
    assert sim > 0.99  # Deben ser casi idénticos

def test_embedding_similarity_semantic():
    norm = ProductNormalizer()
    emb1 = norm.get_embedding("Café molido 500g")
    emb2 = norm.get_embedding("Paquete de café molido 500 gramos")
    sim = cosine_similarity(emb1, emb2)
    assert sim > 0.8  # Deben ser similares semánticamente

def test_embedding_similarity_different():
    norm = ProductNormalizer()
    emb1 = norm.get_embedding("Café molido 500g")
    emb2 = norm.get_embedding("Azúcar refinada 1kg")
    sim = cosine_similarity(emb1, emb2)
    assert sim < 0.8  # Deben ser menos similares
