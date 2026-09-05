# -*- coding: utf-8 -*-
import time
import logging
import json
import pytest
from unittest.mock import MagicMock, patch

from content_safety.checker import kiem_duyet_noi_dung
from content_safety.softener import mem_hoa_noi_dung
from content_safety.pipeline import xu_ly_an_toan_noi_dung, THONG_BAO_AN_TOAN_MAC_DINH
from content_safety.custom_keywords import TU_KHOA_CHAN_CUNG, TU_KHOA_CAN_MEM_HOA
from interpretation_api.orchestrator.main_flow import luan_giai
from ai_module.schemas import AIResponse


def test_1_noi_dung_binh_thuong_qua_duyet():
    clean_text = "Cung M\u1ec7nh c\xf3 sao Thi\xean L\u01b0\u01a1ng t\u1ecda th\u1ee7 l\xe0 ng\u01b0\u1eddi nh\xe2n h\u1eadu, \u0111i\u1ec1m \u0111\u1ea1m."
    res = kiem_duyet_noi_dung(clean_text)
    assert res["qua_duyet"] is True
    assert res["can_mem_hoa"] is False
    assert len(res["danh_sach_cum_tu_can_sua"]) == 0


def test_2_noi_dung_chua_tu_khoa_chan_cung():
    toxic_text = "N\u0103m nay g\u1eb7p h\u1ea1n n\u1eb7ng, ch\u1eafc ch\u1eafn s\u1ebd ch\u1ebft v\xe0 ph\u1ea3i b\u1ecf ti\u1ec1n c\xfang b\xe1i m\u1edbi mong tho\xe1t."
    res = kiem_duyet_noi_dung(toxic_text)
    assert res["qua_duyet"] is False
    assert res["can_mem_hoa"] is False
    assert any("ch\u1eafc ch\u1eafn s\u1ebd ch\u1ebft" in kw for kw in res["tu_khoa_vi_pham"])


def test_3_noi_dung_can_mem_hoa_va_sau_khi_mem_hoa():
    harsh_text = "N\u0103m nay l\xe1 s\u1ed1 cho th\u1ea5y b\u1ea1n ch\u1eafc ch\u1eafn g\u1eb7p \u0111\u1ea1i h\u1ea1n v\xe0 s\u1ef1 nghi\u1ec7p b\u1ebf t\u1eafc ho\xe0n to\xe0n."
    res = kiem_duyet_noi_dung(harsh_text)
    assert res["qua_duyet"] is True
    assert res["can_mem_hoa"] is True
    assert any("ch\u1eafc ch\u1eafn g\u1eb7p \u0111\u1ea1i h\u1ea1n" in kw for kw in res["danh_sach_cum_tu_can_sua"])
    assert any("b\u1ebf t\u1eafc ho\xe0n to\xe0n" in kw for kw in res["danh_sach_cum_tu_can_sua"])

    softened = mem_hoa_noi_dung(harsh_text, res["danh_sach_cum_tu_can_sua"])
    recheck = kiem_duyet_noi_dung(softened)
    assert recheck["qua_duyet"] is True
    assert recheck["can_mem_hoa"] is False


def test_4_moderation_api_phat_hien_vi_pham():
    mock_mod_fn = MagicMock(return_value={
        "vi_pham": True,
        "danh_muc_vi_pham": ["violence", "harassment"],
        "muc_do": {"violence": 0.92}
    })
    text = "V\u0103n b\u1ea3n b\u1ecb b\xe1o vi ph\u1ea1m b\u1edfi Moderation API."
    res = kiem_duyet_noi_dung(text, custom_moderation_fn=mock_mod_fn)
    assert res["qua_duyet"] is False
    assert "violence" in res["danh_muc"]
    assert res["nguon_phat_hien"] == "moderation_api"


def test_5_mem_hoa_that_bai_chuyen_thang_mac_dinh():
    payload = {
        "cau_tra_loi": {
            "noi_dung": "V\u1eadn tr\xecnh ch\u1eafc ch\u1eafn g\u1eb7p \u0111\u1ea1i h\u1ea1n."
        }
    }
    mock_bad_softener = MagicMock(return_value="Sau khi m\u1ec1m h\xf3a v\u1eabn ch\u1ee9a ch\u1eafc ch\u1eafn s\u1ebd ch\u1ebft.")
    with patch("content_safety.pipeline.mem_hoa_noi_dung", mock_bad_softener):
        res = xu_ly_an_toan_noi_dung(payload)

    assert res["cau_tra_loi"]["noi_dung"] == THONG_BAO_AN_TOAN_MAC_DINH
    assert res["kiem_duyet_an_toan"]["da_bi_chan"] is True
    assert mock_bad_softener.call_count == 1


def test_6_xu_ly_an_toan_da_truong_json():
    payload = {
        "cau_tra_loi": {
            "chu_de": "Xem h\u1ea1n - ch\u1eafc ch\u1eafn s\u1ebd ly h\xf4n",
            "noi_dung": "S\u1ef1 nghi\u1ec7p kh\xe1 \u1ed5n \u0111\u1ecbnh nh\u1edd sao Thi\xean L\u01b0\u01a1ng.",
            "ghi_chu": "L\u01b0u \xfd b\u1ebf t\u1eafc ho\xe0n to\xe0n trong th\xe1ng 7."
        }
    }
    res = xu_ly_an_toan_noi_dung(payload)
    assert res["cau_tra_loi"]["chu_de"] == THONG_BAO_AN_TOAN_MAC_DINH
    assert "Thi\xean L\u01b0\u01a1ng" in res["cau_tra_loi"]["noi_dung"]
    assert "b\u1ebf t\u1eafc ho\xe0n to\xe0n" not in res["cau_tra_loi"]["ghi_chu"]


def test_7_log_audit_an_toan_khong_lo_noi_dung(caplog):
    caplog.set_level(logging.INFO)
    sensitive_prompt = "N\u1ed9i dung b\xed m\u1eadt r\u1ea5t nh\u1ea1y c\u1ea3m ch\u1eafc ch\u1eafn s\u1ebd ch\u1ebft."
    payload = {"cau_tra_loi": {"noi_dung": sensitive_prompt}}
    xu_ly_an_toan_noi_dung(payload)

    audit_logs = [record.message for record in caplog.records if "[CONTENT_SAFETY_AUDIT]" in record.message]
    assert len(audit_logs) >= 1
    log_msg = audit_logs[0]
    assert "DA_BI_CHAN" in log_msg
    assert "N\u1ed9i dung b\xed m\u1eadt r\u1ea5t nh\u1ea1y c\u1ea3m" not in log_msg


def test_8_hieu_nang_kiem_duyet_duoi_2_giay():
    long_text = ("L\xe1 s\u1ed1 T\u1eed Vi c\xf3 cung M\u1ec7nh an t\u1ea1i Th\xe2n g\u1eb7p ch\xednh tinh T\u1eed Vi. ") * 20
    start = time.perf_counter()
    res = kiem_duyet_noi_dung(long_text)
    elapsed = time.perf_counter() - start
    assert res["qua_duyet"] is True
    assert elapsed < 1.0


def test_9_tich_hop_luong_luan_giai_orchestrator():
    mock_ai = MagicMock()
    mock_ai.goi_ai_voi_retry.return_value = AIResponse(
        text=json.dumps({
            "chu_de": "T\u1eed Vi",
            "noi_dung": "N\u0103m nay c\xf4ng vi\u1ec7c b\u1ebf t\u1eafc ho\xe0n to\xe0n nh\u01b0ng h\u1eadu v\u1eadn s\u1ebd kh\xe1 h\u01a1n.",
            "muc_do_tin_cay": 0.9
        }),
        provider="mock_gemini",
        tokens_used=150,
        thoi_gian_xu_ly_ms=200,
        thanh_cong=True
    )

    with patch("interpretation_api.orchestrator.main_flow.xac_dinh_he_thong", return_value={"he_thong": "tu_vi", "can_hoi_lai": False, "chua_co_du_lieu": False}):
        with patch("interpretation_api.orchestrator.main_flow.search", return_value=[]):
            res = luan_giai(
                user_id="user_safety_test",
                cau_hoi="Xem cung M\u1ec7nh sao T\u1eed Vi",
                du_lieu_dau_vao={"sao_chu_dao": "T\u1eed Vi"},
                ai_client=mock_ai
            )

    assert res["thanh_cong"] is True
    assert "kiem_duyet_an_toan" in res
    assert res["kiem_duyet_an_toan"]["da_mem_hoa"] is True
    assert "b\u1ebf t\u1eafc ho\xe0n to\xe0n" not in res["cau_tra_loi"]["noi_dung"]
