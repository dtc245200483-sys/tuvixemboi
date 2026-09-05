# -*- coding: utf-8 -*-
"""
B? 8 Test Cases ki?m th? to?n di?n Knowledge Base Ingestion & Vector Store:
1. N?p d? li?u m?u gi? l?p -> dem_so_luong tr? v? ??ng s? l??ng.
2. Idempotent: n?p l?i l?n 2 c?ng d? li?u -> dem_so_luong kh?ng t?ng g?p ??i.
3. Namespace kh?ng c? file d? li?u -> kh?ng crash, b?o c?o r? 'ch?a c? d? li?u'.
4. File JSON c? item sai schema -> b? qua item l?i, ghi v?o danh_sach_loi_neu_co, n?p th?nh c?ng c?c item h?p l?.
5. tao_embedding: 2 c?u t??ng ??ng ng? ngh?a -> Cosine Similarity > 0.7.
6. tao_embedding: 2 c?u kh?c bi?t ng? ngh?a -> Cosine Similarity th?p h?n r? r?t.
7. khoi_tao_collection: 4 namespace t?ch bi?t ??c l?p, kh?ng b? l?n ch?o d? li?u.
8. xoa_du_lieu: x?a item theo ID -> dem_so_luong gi?m ??ng 1, t?m ki?m kh?ng c?n xu?t hi?n.
"""

import os
import json
import pytest
from typing import List, Dict, Any

from knowledge_base.embedding_service import tao_embedding, tinh_cosine_similarity
from knowledge_base.vector_store import (
    khoi_tao_collection,
    them_du_lieu,
    xoa_du_lieu,
    dem_so_luong,
    tim_kiem
)
from knowledge_base.ingest_pipeline import nap_du_lieu_tu_json, nap_toan_bo


@pytest.fixture
def temp_vector_db(tmp_path):
    """T?o th? m?c Vector DB t?m th?i cho t?ng test case."""
    db_dir = str(tmp_path / "test_chroma_db")
    return db_dir


@pytest.fixture
def sample_json_dir(tmp_path):
    """T?o th? m?c ch?a file JSON m?u chu?n schema."""
    json_dir = tmp_path / "sample_json"
    json_dir.mkdir()
    sample_items = [
        {
            "loai": "chinh_tinh",
            "ten": "T? Vi",
            "noi_dung_moi": "T? Vi l? ?? Tinh, thu?c ?m Th?, ch? v? quy?n qu? t?i l?nh ??o v? s? nghi?p vinh hi?n.",
            "nguon_goc": "Tu vi nghiem ly",
            "do_tin_cay": 1.0
        },
        {
            "loai": "chinh_tinh",
            "ten": "Thi?n C?",
            "noi_dung_moi": "Thi?n C? l? Thi?n Tinh, thu?c ?m M?c, ch? v? m?u l??c, tr? tu? v? s? linh ho?t.",
            "nguon_goc": "Tu vi nghiem ly",
            "do_tin_cay": 0.95
        },
        {
            "loai": "chinh_tinh",
            "ten": "Th?i D??ng",
            "noi_dung_moi": "Th?i D??ng l? Quang Minh Tinh, thu?c D??ng H?a, t??ng tr?ng cho m?t tr?i v? quang minh ch?nh ??i.",
            "nguon_goc": "Tu vi nghiem ly",
            "do_tin_cay": 0.95
        }
    ]
    with open(json_dir / "sample_tu_vi.json", "w", encoding="utf-8") as f:
        json.dump(sample_items, f, ensure_ascii=False)
    return str(json_dir)


def test_1_nap_du_lieu_mau_dem_dung_so_luong(sample_json_dir, temp_vector_db):
    """Test 1: N?p d? li?u m?u gi? l?p -> dem_so_luong tr? v? ??ng s? l??ng ?? n?p."""
    res = nap_du_lieu_tu_json(sample_json_dir, "tu_vi", custom_db_path=temp_vector_db)
    assert res["tong_so_item_da_nap"] == 3
    assert res["so_file_da_xu_ly"] == 1
    assert len(res["danh_sach_loi_neu_co"]) == 0

    so_luong = dem_so_luong("tu_vi", custom_db_path=temp_vector_db)
    assert so_luong == 3


def test_2_nap_du_lieu_idempotent_khong_nhan_doi(sample_json_dir, temp_vector_db):
    """Test 2: Ch?y l?i nap_du_lieu_tu_json L?N 2 v?i C?NG d? li?u -> s? l??ng KH?NG t?ng g?p ??i."""
    # L?n 1
    nap_du_lieu_tu_json(sample_json_dir, "tu_vi", custom_db_path=temp_vector_db)
    so_luong_lan_1 = dem_so_luong("tu_vi", custom_db_path=temp_vector_db)
    assert so_luong_lan_1 == 3

    # L?n 2 (c?ng d? li?u)
    nap_du_lieu_tu_json(sample_json_dir, "tu_vi", custom_db_path=temp_vector_db)
    so_luong_lan_2 = dem_so_luong("tu_vi", custom_db_path=temp_vector_db)
    assert so_luong_lan_2 == 3, f"S? l??ng b? nh?n ??i: {so_luong_lan_2} thay v? 3"


def test_3_namespace_khong_co_file_khong_crash(tmp_path, temp_vector_db):
    """Test 3: Namespace KH?NG c? file d? li?u n?o -> kh?ng crash, tr? v? 'ch?a c? d? li?u'."""
    empty_dir = str(tmp_path / "empty_namespace_folder")
    os.makedirs(empty_dir, exist_ok=True)

    res = nap_du_lieu_tu_json(empty_dir, "bat_tu", custom_db_path=temp_vector_db)
    assert res["tong_so_item_da_nap"] == 0
    assert res["so_file_da_xu_ly"] == 0
    assert "ch?a c? d? li?u" in res["ghi_chu"]
    assert dem_so_luong("bat_tu", custom_db_path=temp_vector_db) == 0


def test_4_item_sai_schema_bi_bo_qua_va_ghi_loi(tmp_path, temp_vector_db):
    """Test 4: 1 file JSON c? item SAI schema (thi?u tr??ng) -> ghi l?i, n?p ti?p item h?p l?."""
    mixed_dir = tmp_path / "mixed_json"
    mixed_dir.mkdir()

    items = [
        # Item 1: H?p l?
        {
            "loai": "que_kep",
            "ten": "C?n vi Thi?n",
            "noi_dung_moi": "Qu? Thu?n C?n g?m 6 h?o d??ng, bi?u t??ng c?a Tr?i, c??ng ki?n.",
            "nguon_goc": "Kinh Dich Ngo Tat To",
            "do_tin_cay": 1.0
        },
        # Item 2: L?I (Thi?u tr??ng 'noi_dung_moi' v? 'do_tin_cay')
        {
            "loai": "que_kep",
            "ten": "Kh?n vi ??a"
            # thi?u noi_dung_moi, nguon_goc, do_tin_cay
        },
        # Item 3: H?p l?
        {
            "loai": "que_kep",
            "ten": "Th?y L?i Tru?n",
            "noi_dung_moi": "Qu? Tru?n ch? v? s? gian nan b??c ??u kh?i nghi?p nh?ng t?ch l?y n?i l?c.",
            "nguon_goc": "Kinh Dich Ngo Tat To",
            "do_tin_cay": 0.9
        }
    ]
    with open(mixed_dir / "mixed_kinh_dich.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)

    res = nap_du_lieu_tu_json(str(mixed_dir), "kinh_dich", custom_db_path=temp_vector_db)
    # Item 2 b? b? qua, ch? c? 2 item h?p l? ???c n?p
    assert res["tong_so_item_da_nap"] == 2
    assert len(res["danh_sach_loi_neu_co"]) == 1
    assert "Kh?n vi ??a" in res["danh_sach_loi_neu_co"][0]["item_ten"]

    so_luong = dem_so_luong("kinh_dich", custom_db_path=temp_vector_db)
    assert so_luong == 2


def test_5_tao_embedding_cau_dong_nghia_cosine_similarity_cao():
    """Test 5: 2 c?u c? ? ngh?a g?n gi?ng nhau v? c?ng 1 sao -> cosine similarity > 0.7."""
    cau_1 = "Sao T? Vi l? ?? Tinh ??ng ??u mu?n sao, ch? v? quy?n uy, c?ng danh vinh hi?n v? t?i l?nh ??o."
    cau_2 = "T? Vi l? ng?i sao ho?ng ?? th??ng ??nh, mang t?nh c?ch uy nghi?m, t?n qu? v? s? nghi?p th?ng ti?n."

    vec_1 = tao_embedding(cau_1)
    vec_2 = tao_embedding(cau_2)

    similarity = tinh_cosine_similarity(vec_1, vec_2)
    assert similarity > 0.7, f"?? t??ng ??ng ng? ngh?a th?p ({similarity:.3f} <= 0.7)"


def test_6_tao_embedding_cau_khac_biet_cosine_similarity_thap():
    """Test 6: 2 c?u c? ? ngh?a kh?c bi?t ho?n to?n (sao T? Vi vs qu? C?n) -> ?? t??ng ??ng th?p h?n r? r?t so v?i test 5."""
    cau_tu_vi_1 = "Sao T? Vi l? ?? Tinh ??ng ??u mu?n sao, ch? v? quy?n uy, c?ng danh vinh hi?n v? t?i l?nh ??o."
    cau_tu_vi_2 = "T? Vi l? ng?i sao ho?ng ?? th??ng ??nh, mang t?nh c?ch uy nghi?m, t?n qu? v? s? nghi?p th?ng ti?n."
    cau_que_can = "Qu? Thu?n C?n trong Kinh D?ch g?m s?u h?o to?n d??ng, t??ng tr?ng cho tr?i cao v? kh? d??ng nguy?n th?y."

    vec_tu_vi_1 = tao_embedding(cau_tu_vi_1)
    vec_tu_vi_2 = tao_embedding(cau_tu_vi_2)
    vec_que_can = tao_embedding(cau_que_can)

    similarity_synonym = tinh_cosine_similarity(vec_tu_vi_1, vec_tu_vi_2)
    similarity_distinct = tinh_cosine_similarity(vec_tu_vi_1, vec_que_can)

    # X?c nh?n ?? t??ng ??ng c?u kh?c bi?t th?p h?n r? r?t so v?i c?u ??ng ngh?a (ch?nh l?ch > 0.25)
    assert similarity_synonym > 0.80
    assert similarity_distinct < similarity_synonym - 0.25, (
        f"?? t??ng ??ng kh?c bi?t ({similarity_distinct:.3f}) kh?ng th?p h?n r? r?t so v?i ??ng ngh?a ({similarity_synonym:.3f})"
    )


def test_7_khoi_tao_collection_4_namespace_tach_biet(temp_vector_db):
    """Test 7: 4 namespace t?o ra 4 collection ri?ng bi?t, d? li?u kh?ng b? l?n ch?o."""
    namespaces = ["tu_vi", "kinh_dich", "bat_tu", "nhan_tuong"]

    # Kh?i t?o c? 4 collections
    for ns in namespaces:
        khoi_tao_collection(ns, custom_db_path=temp_vector_db)

    # N?p 1 item v?o 'tu_vi'
    item_tu_vi = [{
        "id": "tu_vi_demo_01",
        "noi_dung_moi": "Sao Thi?n L??ng l? ?m Tinh ch? v? th? tr??ng",
        "metadata": {"loai": "sao", "he_thong": "tu_vi"}
    }]
    them_du_lieu("tu_vi", item_tu_vi, custom_db_path=temp_vector_db)

    # X?c nh?n ch? c? 'tu_vi' c? d? li?u, 3 namespace c?n l?i l? 0
    assert dem_so_luong("tu_vi", custom_db_path=temp_vector_db) == 1
    assert dem_so_luong("kinh_dich", custom_db_path=temp_vector_db) == 0
    assert dem_so_luong("bat_tu", custom_db_path=temp_vector_db) == 0
    assert dem_so_luong("nhan_tuong", custom_db_path=temp_vector_db) == 0


def test_8_xoa_du_lieu_giam_so_luong_va_khong_con_tim_thay(temp_vector_db):
    """Test 8: X?a 1 item theo ID -> dem_so_luong gi?m ??ng 1, search kh?ng c?n xu?t hi?n."""
    item_1 = {
        "id": "nhan_tuong_tam_dao_01",
        "noi_dung_moi": "???ng T?m ??o s?u r? bi?u th? t?nh c?m ch?n th?nh",
        "metadata": {"loai": "chi_tay", "he_thong": "nhan_tuong"}
    }
    item_2 = {
        "id": "nhan_tuong_tri_dao_02",
        "noi_dung_moi": "???ng Tr? ??o th?ng d?i bi?u th? t? duy logic nh?y b?n",
        "metadata": {"loai": "chi_tay", "he_thong": "nhan_tuong"}
    }
    them_du_lieu("nhan_tuong", [item_1, item_2], custom_db_path=temp_vector_db)
    assert dem_so_luong("nhan_tuong", custom_db_path=temp_vector_db) == 2

    # T?m ki?m ban ??u th?y item 1
    tim_ban_dau = tim_kiem("nhan_tuong", "t?nh c?m s?u s?c", top_k=2, custom_db_path=temp_vector_db)
    ids_ban_dau = [res["id"] for res in tim_ban_dau]
    assert "nhan_tuong_tam_dao_01" in ids_ban_dau

    # X?a item 1
    xoa_ok = xoa_du_lieu("nhan_tuong", "nhan_tuong_tam_dao_01", custom_db_path=temp_vector_db)
    assert xoa_ok is True
    assert dem_so_luong("nhan_tuong", custom_db_path=temp_vector_db) == 1

    # T?m ki?m l?i, item 1 kh?ng c?n xu?t hi?n
    tim_lai = tim_kiem("nhan_tuong", "t?nh c?m s?u s?c", top_k=2, custom_db_path=temp_vector_db)
    ids_lai = [res["id"] for res in tim_lai]
    assert "nhan_tuong_tam_dao_01" not in ids_lai
