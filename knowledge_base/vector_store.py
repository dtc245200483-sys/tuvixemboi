# -*- coding: utf-8 -*-
"""
Module Qu?n L? Vector Database ChromaDB (Vector Store)
H? tr? qu?n l? 4 collections/namespaces t?ch bi?t:
- tu_vi: D? li?u sao, cung, c?ch c?c T? Vi ??u S?.
- kinh_dich: D? li?u 64 qu?, h?o t?, tho?n t? Kinh D?ch.
- bat_tu: D? li?u can chi, th?p th?n, d?ng th?n B?t T? T? Tr?.
- nhan_tuong: D? li?u ???ng ch? tay, ng? quan, t??ng m?o Nh?n T??ng H?c.
"""

import os
import sys
from typing import List, Dict, Any, Optional

# N?p c?u h?nh backend ?? l?y vector_db_path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from config import settings
    DEFAULT_DB_PATH = os.path.abspath(settings.vector_db_path)
except Exception:
    DEFAULT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "vector_store"))

from knowledge_base.embedding_service import tao_embedding, tao_embedding_batch

# Cache client theo ???ng d?n db ?? t?i s? d?ng connection
_chroma_clients: Dict[str, Any] = {}


def get_chroma_client(db_path: Optional[str] = None):
    """L?y ChromaDB PersistentClient k?t n?i t?i th? m?c l?u tr? persistent."""
    import chromadb
    target_path = os.path.abspath(db_path) if db_path else DEFAULT_DB_PATH
    os.makedirs(target_path, exist_ok=True)
    if target_path not in _chroma_clients:
        _chroma_clients[target_path] = chromadb.PersistentClient(path=target_path)
    return _chroma_clients[target_path]


def khoi_tao_collection(namespace: str, custom_db_path: Optional[str] = None):
    """
    T?o ho?c l?y collection ChromaDB theo t?n namespace (tu_vi/kinh_dich/bat_tu/nhan_tuong).
    Collection s? d?ng kho?ng c?ch cosine similarity.
    """
    client = get_chroma_client(custom_db_path)
    # T?n collection trong chromadb ch? ch?a ch? c?i th??ng, s?, d?u g?ch d??i
    clean_namespace = namespace.strip().lower()
    collection = client.get_or_create_collection(
        name=clean_namespace,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def them_du_lieu(
    namespace: str,
    danh_sach_item: List[Dict[str, Any]],
    batch_size: int = 50,
    custom_db_path: Optional[str] = None
) -> int:
    """
    Nh?n danh s?ch item, chia l? (batch insert/upsert), t?o embedding h?ng lo?t
    v? l?u v?o ??ng collection theo namespace.
    
    Y?u c?u m?i item:
    - id: str
    - noi_dung_moi: str (t?i li?u/v?n b?n c?n nh?ng vector)
    - metadata: dict (ch?a loai, he_thong, nguon_goc, do_tin_cay...)
    """
    if not danh_sach_item:
        return 0

    collection = khoi_tao_collection(namespace, custom_db_path=custom_db_path)
    tong_so_luong = len(danh_sach_item)
    so_da_them = 0

    for i in range(0, tong_so_luong, batch_size):
        batch = danh_sach_item[i:i + batch_size]

        ids = [str(item["id"]) for item in batch]
        documents = [str(item["noi_dung_moi"]) for item in batch]

        # Chu?n h?a metadata (ChromaDB ch? ch?p nh?n str, int, float, bool)
        metadatas = []
        for item in batch:
            raw_meta = item.get("metadata", {})
            clean_meta = {}
            for k, v in raw_meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                elif v is None:
                    clean_meta[k] = ""
                else:
                    clean_meta[k] = str(v)
            metadatas.append(clean_meta)

        # T?o embedding h?ng lo?t cho to?n b? batch
        embeddings = tao_embedding_batch(documents)

        # S? d?ng upsert ?? ??m b?o t?nh Idempotent (kh?ng t?o tr?ng l?p khi ch?y l?i)
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        so_da_them += len(batch)

    return so_da_them


def xoa_du_lieu(namespace: str, id: str, custom_db_path: Optional[str] = None) -> bool:
    """X?a 1 item kh?i collection theo id."""
    collection = khoi_tao_collection(namespace, custom_db_path=custom_db_path)
    try:
        collection.delete(ids=[str(id)])
        return True
    except Exception as e:
        print(f"[C?NH B?O] L?i khi x?a item {id} kh?i {namespace}: {e}")
        return False


def dem_so_luong(namespace: str, custom_db_path: Optional[str] = None) -> int:
    """??m s? l??ng item hi?n c? trong 1 namespace."""
    collection = khoi_tao_collection(namespace, custom_db_path=custom_db_path)
    return collection.count()


def tim_kiem(
    namespace: str,
    query: str,
    top_k: int = 5,
    filter_dict: Optional[Dict[str, Any]] = None,
    custom_db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    T?m ki?m ng? ngh?a (vector similarity search) trong namespace.
    Tr? v? danh s?ch c?c k?t qu? g?m: id, document, metadata, distance (kho?ng c?ch cosine).
    """
    collection = khoi_tao_collection(namespace, custom_db_path=custom_db_path)
    query_vector = tao_embedding(query)

    query_params = {
        "query_embeddings": [query_vector],
        "n_results": min(top_k, max(1, collection.count())) if collection.count() > 0 else 1
    }
    if filter_dict:
        query_params["where"] = filter_dict

    if collection.count() == 0:
        return []

    results = collection.query(**query_params)

    ket_qua = []
    if results and "ids" in results and results["ids"]:
        for idx in range(len(results["ids"][0])):
            item_id = results["ids"][0][idx]
            doc = results["documents"][0][idx] if "documents" in results and results["documents"] else ""
            meta = results["metadatas"][0][idx] if "metadatas" in results and results["metadatas"] else {}
            dist = results["distances"][0][idx] if "distances" in results and results["distances"] else 0.0
            ket_qua.append({
                "id": item_id,
                "document": doc,
                "metadata": meta,
                "distance": dist,
                "similarity": 1.0 - dist  # Cosine similarity
            })

    return ket_qua
