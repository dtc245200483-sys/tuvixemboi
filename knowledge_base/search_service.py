# -*- coding: utf-8 -*-
"""
Module D?ch V? T?m Ki?m Ng? Ngh?a (Knowledge Base Semantic Search Service)
Ph?c v? Interpretation Agent tra c?u ch?nh x?c tri th?c huy?n h?c theo ??ng namespace,
??m b?o t?nh c? l?p gi?a 4 h? th?ng (T? Vi, Kinh D?ch, B?t T?, Nh?n T??ng).
"""

import time
import logging
from typing import List, Dict, Any, Optional

from knowledge_base.vector_store import tim_kiem

# C?u h?nh logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KnowledgeBaseSearch")

# Danh s?ch 4 namespace h?p l?
VALID_NAMESPACES = {"tu_vi", "kinh_dich", "bat_tu", "nhan_tuong"}


def _kiem_tra_namespace(namespace: str):
    """Ki?m tra t?nh h?p l? c?a namespace b?t bu?c."""
    if not namespace or not isinstance(namespace, str):
        raise ValueError("Tham s? 'namespace' l? b?t bu?c v? ph?i l? chu?i k? t?.")
    clean_ns = namespace.strip().lower()
    if clean_ns not in VALID_NAMESPACES:
        raise ValueError(
            f"Namespace '{namespace}' kh?ng h?p l?. Ch? ch?p nh?n m?t trong c?c namespace: "
            f"{', '.join(sorted(VALID_NAMESPACES))}"
        )
    return clean_ns


def search(
    query: str,
    namespace: str,
    top_k: int = 5,
    nguong_lien_quan: float = 0.5,
    custom_db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    1. T?m ki?m ng? ngh?a trong ??ng collection c?a namespace:
    - T?o embedding cho query.
    - T?m top_k k?t qu? g?n nh?t trong namespace.
    - L?c b? k?t qu? c? ?? li?n quan th?p h?n `nguong_lien_quan`.
    - Tr? v? danh s?ch [{id, ten, noi_dung_moi, nguon_goc, do_tin_cay, do_lien_quan}], s?p x?p gi?m d?n theo ?? li?n quan.
    - Ghi log th?i gian x? l? v? s? l??ng k?t qu?.
    """
    clean_ns = _kiem_tra_namespace(namespace)
    t_start = time.perf_counter()

    if not query or not query.strip():
        return []

    # T?m ki?m trong vector store
    raw_results = tim_kiem(
        namespace=clean_ns,
        query=query,
        top_k=top_k,
        custom_db_path=custom_db_path
    )

    ket_qua = []
    for r in raw_results:
        sim = float(r.get("similarity", 0.0))
        # Ch? gi? l?i k?t qu? ??t ng??ng l?c
        if sim >= nguong_lien_quan:
            meta = r.get("metadata", {})
            ket_qua.append({
                "id": r["id"],
                "ten": meta.get("ten", ""),
                "noi_dung_moi": r.get("document", ""),
                "nguon_goc": meta.get("nguon_goc", ""),
                "do_tin_cay": meta.get("do_tin_cay", 1.0),
                "do_lien_quan": round(sim, 4),
                "metadata": meta
            })

    # S?p x?p gi?m d?n theo ?? li?n quan
    ket_qua.sort(key=lambda x: x["do_lien_quan"], reverse=True)
    ket_qua = ket_qua[:top_k]

    t_elapsed_ms = (time.perf_counter() - t_start) * 1000
    logger.info(
        f"[SEARCH] Query: '{query}' | Namespace: '{clean_ns}' | "
        f"K?t qu?: {len(ket_qua)} (top_k={top_k}) | ?? tr?: {t_elapsed_ms:.2f}ms"
    )

    return ket_qua


def search_da_thuc_the(
    danh_sach_query: List[str],
    namespace: str,
    top_k_moi_query: int = 3,
    nguong_lien_quan: float = 0.5,
    custom_db_path: Optional[str] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    2. Tra c?u nhi?u th?c th? c?ng l?c (VD: c?c sao, cung trong l? s?):
    - G?i `search` cho t?ng query.
    - G?p k?t qu? theo d?ng {query_1: [...], query_2: [...]}.
    - Lo?i b? tr?ng l?p: n?u 1 item xu?t hi?n ? nhi?u query, ?u ti?n g?n cho
      query c? ?? li?n quan (similarity) cao nh?t.
    """
    clean_ns = _kiem_tra_namespace(namespace)
    raw_results = {}

    # 1. T?m ki?m k?t qu? cho t?ng query
    for q in danh_sach_query:
        if not q or not q.strip():
            raw_results[q] = []
            continue

        items = search(
            query=q,
            namespace=clean_ns,
            top_k=top_k_moi_query,
            nguong_lien_quan=nguong_lien_quan,
            custom_db_path=custom_db_path
        )
        raw_results[q] = items

    # 2. X?c ??nh query c? ?? li?n quan cao nh?t cho m?i item ID
    best_query_for_item = {}  # item_id -> (best_query, max_similarity)
    for q, items in raw_results.items():
        for item in items:
            item_id = item["id"]
            sim = item["do_lien_quan"]
            if item_id not in best_query_for_item or sim > best_query_for_item[item_id][1]:
                best_query_for_item[item_id] = (q, sim)

    # 3. G?p k?t qu? v? lo?i b? tr?ng l?p (ch? gi? ? query ph? h?p nh?t)
    tong_hop = {q: [] for q in danh_sach_query}
    for q, items in raw_results.items():
        for item in items:
            item_id = item["id"]
            if best_query_for_item.get(item_id, (None, 0))[0] == q:
                tong_hop[q].append(item)

    return tong_hop


def search_uu_tien_nguon(
    query: str,
    namespace: str,
    top_k: int = 5,
    nguong_lien_quan: float = 0.4,
    custom_db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    3. T?m ki?m ?u ti?n ngu?n:
    - ?u ti?n x?p c?c item c? `do_tin_cay = 'kinh_dien'` (ho?c ?? tin c?y tuy?t ??i >= 0.99) l?n tr??c,
      d? ?? li?n quan vector c? th? th?p h?n ??i ch?t so v?i ngu?n `tham_khao`.
    - ?p d?ng khi c?n t?nh ch?nh x?c h?c thu?t cao h?n.
    """
    clean_ns = _kiem_tra_namespace(namespace)
    
    # L?y t?p ?ng vi?n r?ng h?n (top_k * 3) ?? c? ?? item cho re-ranking
    pool_size = max(top_k * 3, 10)
    candidates = search(
        query=query,
        namespace=clean_ns,
        top_k=pool_size,
        nguong_lien_quan=nguong_lien_quan,
        custom_db_path=custom_db_path
    )

    def is_kinh_dien(item: Dict[str, Any]) -> bool:
        dtc = item.get("do_tin_cay", "")
        if isinstance(dtc, str):
            return dtc.strip().lower() in ["kinh_dien", "kinh_?i?n"]
        elif isinstance(dtc, (int, float)):
            return float(dtc) >= 0.99
        return False

    # S?p x?p ?u ti?n:
    # 1. Ngu?n kinh ?i?n tr??c (True -> 0, False -> 1)
    # 2. ?? li?n quan gi?m d?n
    candidates.sort(key=lambda it: (0 if is_kinh_dien(it) else 1, -it["do_lien_quan"]))

    return candidates[:top_k]
