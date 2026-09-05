# -*- coding: utf-8 -*-
"""
Pipeline N?p D? Li?u V?o Vector Database (Knowledge Base Ingest Pipeline)
??c d? li?u tri th?c ?? chu?n h?a t? Data Training Agent, ki?m tra t?nh h?p l? schema,
v? n?p v?o ChromaDB theo 4 namespace t?ch bi?t (tu_vi, kinh_dich, bat_tu, nhan_tuong).
"""

import os
import sys
import json
import hashlib
from typing import Dict, List, Any, Optional

DATA_TRAINING_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Data_training"))
SYSTEMS = ["tu_vi", "kinh_dich", "bat_tu", "nhan_tuong"]

from knowledge_base.vector_store import them_du_lieu, dem_so_luong, khoi_tao_collection

# C?c tr??ng b?t bu?c trong schema c?a Data Training Agent
REQUIRED_SCHEMA_FIELDS = ["loai", "ten", "noi_dung_moi", "nguon_goc", "do_tin_cay"]


def tao_item_id(namespace: str, item: Dict[str, Any], fallback_idx: int) -> str:
    """T?o ??nh danh duy nh?t v? c? ??nh (idempotent ID) cho t?ng item tri th?c."""
    ten = str(item.get("ten", "")).strip().lower().replace(" ", "_")
    loai = str(item.get("loai", "")).strip().lower().replace(" ", "_")
    if ten:
        raw_key = f"{namespace}_{loai}_{ten}"
    else:
        raw_key = f"{namespace}_{loai}_{fallback_idx}"
    # Hash ng?n g?n ?? ID an to?n tuy?t ??i v?i k? t? ??c bi?t
    h = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]
    return f"{namespace}_{ten}_{h}" if ten else f"{namespace}_{h}"


def nap_du_lieu_tu_json(
    duong_dan_thu_muc: str,
    namespace: str,
    custom_db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Qu?t to?n b? file JSON trong `duong_dan_thu_muc`, x?c th?c schema,
    v? n?p v?o Vector Database cho `namespace`.
    
    Y?u c?u k? thu?t:
    1. N?u namespace kh?ng c? file d? li?u n?o -> ghi ch? 'ch?a c? d? li?u', KH?NG crash.
    2. N?u item thi?u tr??ng b?t bu?c -> ghi v?o danh_sach_loi_neu_co, b? qua item ??,
       kh?ng l?m crash to?n b? qu? tr?nh n?p c?c item h?p l? kh?c.
    3. Idempotent: ch?y nhi?u l?n kh?ng nh?n ??i b?n ghi (s? d?ng ID c? ??nh v? upsert).
    """
    clean_ns = namespace.strip().lower()
    report = {
        "namespace": clean_ns,
        "tong_so_item_da_nap": 0,
        "so_file_da_xu_ly": 0,
        "danh_sach_loi_neu_co": [],
        "ghi_chu": ""
    }

    if not os.path.exists(duong_dan_thu_muc):
        report["ghi_chu"] = "ch?a c? d? li?u (th? m?c kh?ng t?n t?i)"
        return report

    json_files = [f for f in os.listdir(duong_dan_thu_muc) if f.lower().endswith(".json")]
    if not json_files:
        report["ghi_chu"] = "ch?a c? d? li?u (kh?ng t?m th?y file JSON)"
        return report

    items_to_ingest = []
    total_files_processed = 0

    for fname in json_files:
        fpath = os.path.join(duong_dan_thu_muc, fname)
        total_files_processed += 1

        try:
            with open(fpath, "r", encoding="utf-8") as fp:
                raw_data = json.load(fp)
        except Exception as e:
            report["danh_sach_loi_neu_co"].append({
                "file": fname,
                "item_index": None,
                "loi": f"Kh?ng th? ??c file JSON: {str(e)}"
            })
            continue

        if isinstance(raw_data, dict):
            # N?u JSON l? 1 object b?c danh s?ch
            if "items" in raw_data and isinstance(raw_data["items"], list):
                item_list = raw_data["items"]
            elif "data" in raw_data and isinstance(raw_data["data"], list):
                item_list = raw_data["data"]
            else:
                item_list = [raw_data]
        elif isinstance(raw_data, list):
            item_list = raw_data
        else:
            report["danh_sach_loi_neu_co"].append({
                "file": fname,
                "item_index": None,
                "loi": "??nh d?ng g?c c?a file JSON kh?ng ph?i List ho?c Dict."
            })
            continue

        for idx, it in enumerate(item_list):
            if not isinstance(it, dict):
                report["danh_sach_loi_neu_co"].append({
                    "file": fname,
                    "item_index": idx,
                    "loi": "Item kh?ng ph?i c?u tr?c Dictionary."
                })
                continue

            # Ki?m tra Schema validation
            missing_fields = [fld for fld in REQUIRED_SCHEMA_FIELDS if fld not in it or it[fld] is None or str(it[fld]).strip() == ""]
            if missing_fields:
                report["danh_sach_loi_neu_co"].append({
                    "file": fname,
                    "item_index": idx,
                    "item_ten": it.get("ten", "Kh?ng r?"),
                    "loi": f"Thi?u c?c tr??ng b?t bu?c trong schema: {', '.join(missing_fields)}"
                })
                # B? qua item l?i, KH?NG crash, ti?p t?c x? l? c?c item h?p l? kh?c
                continue

            # Item h?p l? -> chu?n h?a ??nh d?ng l?u tr? Vector DB
            deterministic_id = tao_item_id(clean_ns, it, idx)
            doc_text = f"[{clean_ns.upper()}] {it['ten']} ({it['loai']}): {it['noi_dung_moi']}"

            metadata = {
                "loai": str(it["loai"]),
                "ten": str(it["ten"]),
                "he_thong": clean_ns,
                "nguon_goc": str(it["nguon_goc"]),
                "do_tin_cay": float(it["do_tin_cay"]) if isinstance(it["do_tin_cay"], (int, float)) else 1.0,
                "file_nguon": fname
            }
            # Th?m c?c tr??ng m? r?ng n?u c? (v? d? v? tr? trong nh?n t??ng)
            for extra_key in ["vi_tri", "cung_vi", "chu_de"]:
                if extra_key in it and it[extra_key]:
                    metadata[extra_key] = str(it[extra_key])

            items_to_ingest.append({
                "id": deterministic_id,
                "noi_dung_moi": doc_text,
                "metadata": metadata
            })

    # N?p to?n b? item h?p l? v?o collection theo batch
    if items_to_ingest:
        so_da_nap = them_du_lieu(clean_ns, items_to_ingest, batch_size=50, custom_db_path=custom_db_path)
        report["tong_so_item_da_nap"] = so_da_nap
    else:
        report["tong_so_item_da_nap"] = 0

    report["so_file_da_xu_ly"] = total_files_processed
    return report


def nap_toan_bo(
    custom_root: Optional[str] = None,
    custom_db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Qu?t v? n?p to?n b? 4 namespace tri th?c huy?n h?c t? th? m?c `rewritten/`.
    T?ng h?p b?o c?o s? l??ng item ?? n?p tr?n t?ng h? th?ng.
    """
    base_root = custom_root or os.path.join(DATA_TRAINING_ROOT, "rewritten")
    tong_hop_bao_cao = {
        "thoi_gian": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cac_he_thong": {},
        "tong_so_item_toan_he_thong": 0
    }

    for sys_name in SYSTEMS:
        sys_folder = os.path.join(base_root, sys_name)
        res = nap_du_lieu_tu_json(sys_folder, sys_name, custom_db_path=custom_db_path)
        tong_hop_bao_cao["cac_he_thong"][sys_name] = res
        tong_hop_bao_cao["tong_so_item_toan_he_thong"] += res["tong_so_item_da_nap"]

    return tong_hop_bao_cao
