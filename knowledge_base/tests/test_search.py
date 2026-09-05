# -*- coding: utf-8 -*-
"""
B? 8 Test Cases ki?m th? to?n di?n Semantic Search Service (RAG Search):
1. Search c?u h?i li?n quan tr?c ti?p -> item xu?t hi?n trong top k?t qu?.
2. Search c?u h?i ho?n to?n kh?ng li?n quan -> tr? v? r?ng do d??i ng??ng l?c.
3. Namespace kh?ng h?p l? -> raise ValueError r? r?ng.
4. search_da_thuc_the v?i 3 query -> c?u tr?c dict ch?nh x?c, kh?ng l?n k?t qu?.
5. T?nh c? l?p namespace -> search trong tu_vi KH?NG bao gi? tr? v? item c?a bat_tu.
6. search_uu_tien_nguon -> item 'kinh_dien' ???c ?u ti?n x?p tr?n item 'tham_khao'.
7. Test hi?u n?ng t?m ki?m -> ?? tr? d??i 500ms.
8. Test top_k -> tr? v? t?i ?a s? l??ng top_k y?u c?u.
"""

import time
import pytest
from typing import List, Dict, Any

from knowledge_base.vector_store import them_du_lieu, khoi_tao_collection, dem_so_luong
from knowledge_base.search_service import search, search_da_thuc_the, search_uu_tien_nguon


@pytest.fixture
def isolated_db(tmp_path):
    """T?o database vector t?m th?i bi?t l?p cho test search."""
    db_path = str(tmp_path / "search_chroma_db")
    
    # N?p s?n m?t s? item v?o 'tu_vi'
    items_tu_vi = [
        {
            "id": "tu_vi_star_01",
            "noi_dung_moi": "[TU_VI] T? Vi (sao): ?? Tinh thu?c ?m Th?, bi?u t??ng ho?ng ??, l?nh ??o quy?n uy v? c?ng danh ph? qu?.",
            "metadata": {"ten": "T? Vi", "loai": "chinh_tinh", "he_thong": "tu_vi", "nguon_goc": "Tu Vi Dau So Toan Thu", "do_tin_cay": "kinh_dien"}
        },
        {
            "id": "tu_vi_star_02",
            "noi_dung_moi": "[TU_VI] Thi?n C? (sao): Thi?n Tinh thu?c ?m M?c, tr? tu? c? m?u, tham m?u ho?ch ??nh linh ho?t.",
            "metadata": {"ten": "Thi?n C?", "loai": "chinh_tinh", "he_thong": "tu_vi", "nguon_goc": "Tu Vi Dau So Toan Thu", "do_tin_cay": "kinh_dien"}
        },
        {
            "id": "tu_vi_star_03",
            "noi_dung_moi": "[TU_VI] Th?i D??ng (sao): Quang Minh Tinh thu?c D??ng H?a, bi?u t??ng m?t tr?i, quang minh ch?nh ??i.",
            "metadata": {"ten": "Th?i D??ng", "loai": "chinh_tinh", "he_thong": "tu_vi", "nguon_goc": "Tu Vi Nghiem Ly", "do_tin_cay": "tham_khao"}
        },
        {
            "id": "tu_vi_star_04",
            "noi_dung_moi": "[TU_VI] V? Kh?c (sao): T?i Tinh thu?c ?m Kim, qu? quy?t d?ng m?nh, gi?i qu?n l? t?i ch?nh bu?n b?n.",
            "metadata": {"ten": "V? Kh?c", "loai": "chinh_tinh", "he_thong": "tu_vi", "nguon_goc": "Tu Vi Nghiem Ly", "do_tin_cay": "tham_khao"}
        }
    ]
    them_du_lieu("tu_vi", items_tu_vi, custom_db_path=db_path)
    return db_path


def test_1_search_cau_hoi_truc_tiep_xuat_hien_top(isolated_db):
    """Test 1: Search c?u h?i li?n quan tr?c ti?p -> item xu?t hi?n trong top k?t qu?."""
    results = search(
        query="Sao T? Vi ?? Tinh ch? v? quy?n uy l?nh ??o v? s? nghi?p ho?ng ??",
        namespace="tu_vi",
        top_k=2,
        nguong_lien_quan=0.4,
        custom_db_path=isolated_db
    )
    assert len(results) > 0
    # X?c nh?n item T? Vi xu?t hi?n trong top k?t qu?
    assert any(item["ten"] == "T? Vi" for item in results)
    assert results[0]["ten"] == "T? Vi"
    assert results[0]["do_lien_quan"] >= 0.4


def test_2_search_cau_hoi_khong_lien_quan_tra_ve_rong(isolated_db):
    """Test 2: Search c?u h?i ho?n to?n kh?ng li?n quan -> tr? v? r?ng do d??i ng??ng l?c."""
    results = search(
        query="C?ch s?a l?i m?n h?nh xanh m?y t?nh Windows v? thay ram ddr5",
        namespace="tu_vi",
        top_k=5,
        nguong_lien_quan=0.75,  # Ng??ng l?c cao
        custom_db_path=isolated_db
    )
    assert len(results) == 0, "Kh?ng ???c tr? v? k?t qu? kh?ng li?n quan khi d??i ng??ng"


def test_3_namespace_khong_hop_le_raise_exception(isolated_db):
    """Test 3: Truy?n namespace kh?ng h?p l? -> raise ValueError r? r?ng."""
    with pytest.raises(ValueError) as exc_info:
        search(query="Sao T? Vi", namespace="xem_tuong", custom_db_path=isolated_db)
    assert "Namespace 'xem_tuong' kh?ng h?p l?" in str(exc_info.value)

    with pytest.raises(ValueError):
        search(query="Sao T? Vi", namespace="", custom_db_path=isolated_db)


def test_4_search_da_thuc_the_cau_truc_chinh_xac(isolated_db):
    """Test 4: search_da_thuc_the v?i 3 query -> tr? v? ??ng c?u tr?c dict, kh?ng l?n k?t qu?."""
    queries = [
        "Sao Thi?n C? ch? v? tr? tu? c? m?u",
        "Sao V? Kh?c ch? v? t?i ch?nh bu?n b?n",
        "Sao Th?i D??ng quang minh ch?nh ??i"
    ]
    res_dict = search_da_thuc_the(
        danh_sach_query=queries,
        namespace="tu_vi",
        top_k_moi_query=2,
        nguong_lien_quan=0.35,
        custom_db_path=isolated_db
    )
    assert isinstance(res_dict, dict)
    assert len(res_dict) == 3
    for q in queries:
        assert q in res_dict
        assert isinstance(res_dict[q], list)

    # Query 1 v? tr? tu? c? m?u -> Thi?n C?
    assert any(item["ten"] == "Thi?n C?" for item in res_dict[queries[0]])
    # Query 2 v? t?i ch?nh -> V? Kh?c
    assert any(item["ten"] == "V? Kh?c" for item in res_dict[queries[1]])
    # Query 3 v? quang minh -> Th?i D??ng
    assert any(item["ten"] == "Th?i D??ng" for item in res_dict[queries[2]])


def test_5_co_lap_namespace_tuyet_doi(tmp_path):
    """Test 5: N?p d? li?u v?o tu_vi v? bat_tu -> search tu_vi KH?NG l?n bat_tu."""
    db_path = str(tmp_path / "cross_check_db")
    
    # N?p 1 item c? ch?a ch? 'H?a' v?o tu_vi
    them_du_lieu("tu_vi", [{
        "id": "tu_vi_thai_duong",
        "noi_dung_moi": "Th?i D??ng l? D??ng H?a trong T? Vi ??u S?",
        "metadata": {"ten": "Th?i D??ng", "he_thong": "tu_vi"}
    }], custom_db_path=db_path)

    # N?p 1 item c?ng c? ch?a ch? 'H?a' v?o bat_tu
    them_du_lieu("bat_tu", [{
        "id": "bat_tu_binh_hoa",
        "noi_dung_moi": "B?nh H?a l? D??ng H?a trong B?t T? T? Tr?",
        "metadata": {"ten": "B?nh H?a", "he_thong": "bat_tu"}
    }], custom_db_path=db_path)

    # T?m ki?m 'D??ng H?a' trong namespace 'tu_vi'
    results_tu_vi = search(query="D??ng H?a", namespace="tu_vi", top_k=5, nguong_lien_quan=0.2, custom_db_path=db_path)
    # X?c nh?n 100% k?t qu? tr? v? ch? thu?c tu_vi, kh?ng ch?a ID c?a bat_tu
    assert len(results_tu_vi) == 1
    assert results_tu_vi[0]["id"] == "tu_vi_thai_duong"
    assert results_tu_vi[0]["id"] != "bat_tu_binh_hoa"

    # T?m ki?m trong namespace 'bat_tu'
    results_bat_tu = search(query="D??ng H?a", namespace="bat_tu", top_k=5, nguong_lien_quan=0.2, custom_db_path=db_path)
    assert len(results_bat_tu) == 1
    assert results_bat_tu[0]["id"] == "bat_tu_binh_hoa"


def test_6_search_uu_tien_nguon_kinh_dien_hon_tham_khao(tmp_path):
    """Test 6: search_uu_tien_nguon -> ngu?n 'kinh_dien' x?p tr??c ngu?n 'tham_khao'."""
    db_path = str(tmp_path / "ranking_db")

    # Item A: Ngu?n tham kh?o nh?ng query tr?ng s?t c?u ch?
    item_tham_khao = {
        "id": "item_tk",
        "noi_dung_moi": "Sao C? M?n l? ?m Tinh ch? v? ng?n ng? v? th? phi kh?u thi?t.",
        "metadata": {"ten": "C? M?n", "do_tin_cay": "tham_khao", "nguon_goc": "Blog Phong Thuy"}
    }
    # Item B: Ngu?n kinh ?i?n
    item_kinh_dien = {
        "id": "item_kd",
        "noi_dung_moi": "C? M?n B?c ??u ?? Nh? Tinh, thu?c ?m Th?y, ch??ng qu?n th? phi ??m ti?u.",
        "metadata": {"ten": "C? M?n To?n Th?", "do_tin_cay": "kinh_dien", "nguon_goc": "Tu Vi Dau So Toan Thu"}
    }
    them_du_lieu("tu_vi", [item_tham_khao, item_kinh_dien], custom_db_path=db_path)

    # G?i search_uu_tien_nguon
    results = search_uu_tien_nguon(
        query="Sao C? M?n ch? v? th? phi kh?u thi?t",
        namespace="tu_vi",
        top_k=2,
        nguong_lien_quan=0.3,
        custom_db_path=db_path
    )
    assert len(results) == 2
    # Item kinh_dien ph?i x?p ? v? tr? ??u ti?n
    assert results[0]["id"] == "item_kd"
    assert results[0]["do_tin_cay"] == "kinh_dien"


def test_7_hieu_nang_search_duoi_500ms(isolated_db):
    """Test 7: ?o th?i gian ch?y search -> x?c nh?n ph?n h?i d??i 500ms."""
    t_start = time.perf_counter()
    results = search(
        query="? ngh?a sao Thi?n C? t?i cung M?nh",
        namespace="tu_vi",
        top_k=3,
        nguong_lien_quan=0.3,
        custom_db_path=isolated_db
    )
    elapsed_ms = (time.perf_counter() - t_start) * 1000

    assert len(results) > 0
    # Th?i gian ph?n h?i ph?i d??i 500ms
    assert elapsed_ms < 500.0, f"Th?i gian t?m ki?m v??t qu? 500ms: {elapsed_ms:.2f}ms"


def test_8_top_k_tra_ve_dung_so_luong(isolated_db):
    """Test 8: G?i search v?i top_k=3 -> tr? v? ??ng t?i ?a 3 k?t qu?."""
    results = search(
        query="C?c ch?nh tinh trong T? Vi",
        namespace="tu_vi",
        top_k=3,
        nguong_lien_quan=0.1,  # Ng??ng th?p ?? l?y t?i ?a
        custom_db_path=isolated_db
    )
    assert len(results) <= 3
