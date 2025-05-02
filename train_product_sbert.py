"""
Entrenamiento de SentenceTransformer para similitud semántica de productos.
Genera ejemplos positivos y negativos, entrena el modelo y guarda el modelo ajustado.
"""
from sentence_transformers import SentenceTransformer, InputExample, losses, models
from torch.utils.data import DataLoader
import os

# 1. Modelo base multilingüe
base_model = 'paraphrase-multilingual-MiniLM-L12-v2'

# 2. Ejemplos de entrenamiento (pares positivos y negativos) desde archivo externo
import json

examples_path = os.path.join(os.path.dirname(__file__), 'train_examples.jsonl')
train_examples = []
with open(examples_path, 'r', encoding='utf-8') as f:
    for line in f:
        ex = json.loads(line)
        train_examples.append(InputExample(texts=ex['texts'], label=ex['label']))

# 3. Cargar modelo y preparar dataloader
model = SentenceTransformer(base_model)
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=2)
train_loss = losses.CosineSimilarityLoss(model)

# 4. Entrenar (más epochs para refuerzo)
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=15,
    warmup_steps=10,
    show_progress_bar=True
)

# 5. Guardar modelo ajustado
output_dir = os.path.join(os.path.dirname(__file__), 'product_sbert_model')
model.save(output_dir)
print(f"Modelo ajustado guardado en {output_dir}")
