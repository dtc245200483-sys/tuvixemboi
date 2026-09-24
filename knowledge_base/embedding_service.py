# -*- coding: utf-8 -*-
"""
Module Embedding Service ?a Ng?n Ng? (Multilingual Embedding Service)
H? tr? t?i ?u ti?ng Vi?t c? thu?t ng? chuy?n m?n H?n Vi?t (T? Vi, Kinh D?ch, B?t T?, Nh?n T??ng).
Model m?c ??nh: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (h? tr? 50+ ng?n ng?).
"""

import numpy as np
from typing import List, Dict, Union, Optional, Any
# Model đa ngôn ngữ tối ưu tiếng Việt và Hán Việt
DEFAULT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

import os
import logging

logger = logging.getLogger("embedding_service")
_model_instance: Optional[Any] = None


def is_embedding_disabled() -> bool:
    val = os.getenv("ENABLE_EMBEDDING", "").strip().lower()
    if val == "true":
        return False
    if val == "false":
        return True
    # Mặc định tắt trên Render container để tránh tràn 512MB RAM gây sập server (502 Bad Gateway)
    if os.getenv("RENDER") or os.getenv("IS_CONTAINER"):
        return True
    return False


def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME):
    """Khởi tạo hoặc lấy instance model theo mô hình Singleton để tránh load lại nhiều lần."""
    global _model_instance
    if is_embedding_disabled():
        logger.info("[EMBEDDING] Mô hình embedding bị tắt để bảo toàn RAM.")
        return None
    if _model_instance is None:
        try:
            from sentence_transformers import SentenceTransformer
            try:
                # Tối ưu tải nhanh từ cache offline, tránh request HEAD mạng làm chậm khởi động
                _model_instance = SentenceTransformer(model_name, local_files_only=True)
            except Exception:
                _model_instance = SentenceTransformer(model_name)
        except Exception as e:
            logger.warning(f"[EMBEDDING] Không thể tải model {model_name}: {e}")
            return None
    return _model_instance


_embedding_cache: Dict[str, List[float]] = {}


def tao_embedding(text: str, model_name: str = DEFAULT_MODEL_NAME) -> List[float]:
    """
    Tạo vector embedding cho 1 câu hoặc đoạn văn bản (có bộ nhớ đệm LRU).
    Output: Danh sách các số thực (float vector, độ dài 384).
    """
    clean_text = text.strip() if text else " "
    cache_key = f"{model_name}:{clean_text}"
    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]

    model = get_embedding_model(model_name)
    if model is None:
        return [0.0] * 384
    emb = model.encode(clean_text, convert_to_numpy=True, normalize_embeddings=True)
    res = emb.tolist()
    if len(_embedding_cache) < 2048:
        _embedding_cache[cache_key] = res
    return res


def tao_embedding_batch(texts: List[str], model_name: str = DEFAULT_MODEL_NAME, batch_size: int = 32) -> List[List[float]]:
    """
    T?o vector embedding theo l? (batch) ?? t?i ?u t?c ?? t?nh to?n song song,
    tr?nh g?i tu?n t? t?ng item.
    Output: Danh s?ch c?c vector.
    """
    if not texts:
        return []

    # X? l? chu?i r?ng n?u c?
    clean_texts = [t if t and t.strip() else " " for t in texts]

    model = get_embedding_model(model_name)
    if model is None:
        return [[0.0] * 384 for _ in clean_texts]
    embeddings = model.encode(
        clean_texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embeddings.tolist()


def tinh_cosine_similarity(vec1: Union[List[float], np.ndarray], vec2: Union[List[float], np.ndarray]) -> float:
    """T?nh ?? t??ng ??ng Cosine gi?a 2 vector (k?t qu? t? -1.0 ??n 1.0)."""
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
