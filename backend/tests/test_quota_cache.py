# -*- coding: utf-8 -*-
"""
B\u1ed9 10 Test Cases ki\u1ec3m th\u1eed to\xe0n di\u1ec7n Usage Quota & Interpretation Cache:
1. User m\u1edbi l\u1ea7n \u0111\u1ea7u g\u1ecdi quota -> t\u1ea1o b\u1ea3n ghi m\u1edbi, con_han_muc = True, so_luot_da_dung = 1.
2. G\u1ecdi li\xean ti\u1ebfp \u0111\u1ebfn gi\u1edbi h\u1ea1n -> l\u1ea7n cu\u1ed1i v\u1eabn con_han_muc = True.
3. G\u1ecdi v\u01b0\u1ee3t qu\xe1 gi\u1edbi h\u1ea1n -> con_han_muc = False.
4. Race Condition Test: g\u1ecdi \u0111\u1ed3ng th\u1eddi t\u1eeb nhi\u1ec1u lu\u1ed3ng (concurrent threads) -> s\u1ed1 l\u01b0\u1ee3t \u0111\u01b0\u1ee3c t\u0103ng ch\xednh x\xe1c tuy\u1ec7t \u0111\u1ed1i.
5. Quota reset theo ng\xe0y m\u1edbi -> b\u1ea3n ghi ng\xe0y h\xf4m qua \u0111\u1ea7y kh\xf4ng \u1ea3nh h\u01b0\u1edfng \u0111\u1ebfn ng\xe0y h\xf4m nay.
6. Cache lu\u1eadn gi\u1ea3i -> g\u1ecdi l\u1ea7n 1 l\u01b0u cache, l\u1ea7n 2 c\xf9ng l\xe1 s\u1ed1 l\u1ea5y t\u1eeb cache, AI g\u1ecdi \u0111\xfang 1 l\u1ea7n.
7. Cache qu\xe1 h\u1ea1n TTL -> b\u1ecf qua cache c\u0169, ch\u1ea1y l\u1ea1i lu\u1ed3ng \u0111\u1ea7y \u0111\u1ee7.
8. xoa_cache_theo_he_thong -> x\xf3a tu_vi th\xec bat_tu kh\xf4ng b\u1ecb \u1ea3nh h\u01b0\u1edfng.
9. C\xe2u h\u1ecfi chat t\u1ef1 do kh\xf4ng ph\u1ea3i t\u1ed5ng quan -> kh\xf4ng d\xf9ng cache, lu\xf4n lu\u1eadn gi\u1ea3i m\u1edbi.
10. Th\u1ee9 t\u1ef1 t\xedch h\u1ee3p: cache tr\u01b0\u1edbc -> n\u1ebfu kh\xf4ng c\xf3 m\u1edbi ki\u1ec3m tra quota -> c\xf2n quota m\u1edbi g\u1ecdi AI.
"""

import uuid
import json
import time
from datetime import date, datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base
from db.models import User, UsageQuota, InterpretationCache
from middleware.quota_service import kiem_tra_va_tang_quota, lay_thong_tin_quota
from interpretation_api.orchestrator.cache_service import (
    tao_cache_key,
    lay_ket_qua_cache,
    luu_ket_qua_cache,
    xoa_cache_theo_he_thong
)
from interpretation_api.orchestrator.main_flow import luan_giai
from ai_module.schemas import AIResponse


@pytest.fixture
def test_db():
    """T\u1ea1o SQLite database d\xf9ng StaticPool \u0111\u1ec3 chia s\u1ebb memory gi\u1eefa c\xe1c thread."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # T\u1ea1o user th\u1eed nghi\u1ec7m
    uid = uuid.UUID("22222222-2222-2222-2222-222222222222")
    user = User(
        id=uid,
        email="quota_test@example.com",
        password_hash="hashed_pw",
        is_active=True
    )
    session.add(user)
    session.commit()

    yield session, Session, uid
    session.close()


def test_1_user_moi_tang_quota_lan_dau(test_db):
    session, _, uid = test_db
    res = kiem_tra_va_tang_quota(user_id=uid, db=session)
    assert res["con_han_muc"] is True
    assert res["so_luot_da_dung"] == 1
    assert res["so_luot_con_lai"] == res["gioi_han_ngay"] - 1


def test_2_goi_den_khi_dat_dung_gioi_han(test_db):
    session, _, uid = test_db
    with patch("middleware.quota_service.settings.ai_daily_quota_free_user", 5):
        for i in range(1, 6):
            res = kiem_tra_va_tang_quota(user_id=uid, db=session)
            assert res["con_han_muc"] is True
            assert res["so_luot_da_dung"] == i

        assert res["so_luot_con_lai"] == 0


def test_3_goi_them_khi_het_han_muc(test_db):
    session, _, uid = test_db
    with patch("middleware.quota_service.settings.ai_daily_quota_free_user", 3):
        for _ in range(3):
            kiem_tra_va_tang_quota(user_id=uid, db=session)

        # L\u1ea7n th\u1ee9 4 -> H\u1ebft h\u1ea1n m\u1ee9c
        res_over = kiem_tra_va_tang_quota(user_id=uid, db=session)
        assert res_over["con_han_muc"] is False
        assert "h\u1ebft l\u01b0\u1ee3t" in res_over["thong_bao"]
        assert res_over["so_luot_da_dung"] == 3


def test_4_race_condition_concurrent_threads(test_db):
    _, SessionCls, uid = test_db
    num_requests = 10
    limit = 20

    def worker_call():
        sess = SessionCls()
        try:
            with patch("middleware.quota_service.settings.ai_daily_quota_free_user", limit):
                r = kiem_tra_va_tang_quota(user_id=uid, db=sess)
                return r["con_han_muc"]
        finally:
            sess.close()

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda _: worker_call(), range(num_requests)))

    # To\xe0n b\u1ed9 c\xe1c g\u1ecdi \u0111\u1ec1u th\xe0nh c\xf4ng
    assert all(results)
    
    # Ki\u1ec3m tra s\u1ed1 l\u01b0\u1ee3t ch\xednh x\xe1c tuy\u1ec7t \u0111\u1ed1i trong DB
    verify_sess = SessionCls()
    rec = verify_sess.query(UsageQuota).filter(UsageQuota.user_id == uid, UsageQuota.ngay == date.today()).first()
    assert rec.so_luot_da_dung == num_requests
    verify_sess.close()


def test_5_quota_reset_theo_ngay_moi(test_db):
    session, _, uid = test_db
    yesterday = date.today() - timedelta(days=1)

    # Gi\u1ea3 l\u1eadp h\xf4m qua \u0111\xe3 h\u1ebft quota (da_dung = 50)
    old_q = UsageQuota(
        id=uuid.uuid4(),
        user_id=uid,
        ngay=yesterday,
        so_luot_da_dung=50
    )
    session.add(old_q)
    session.commit()

    # H\xf4m nay g\u1ecdi l\u1ea7n \u0111\u1ea7u -> ph\u1ea3i c\xf2n h\u1ea1n m\u1ee9c v\xe0 so_luot = 1
    res = kiem_tra_va_tang_quota(user_id=uid, db=session)
    assert res["con_han_muc"] is True
    assert res["so_luot_da_dung"] == 1


def test_6_cache_luan_giai_khong_goi_ai_lan_2(test_db):
    session, _, uid = test_db
    ref_id = "laso_sample_cache_01"
    
    mock_ai = MagicMock()
    mock_ai.goi_ai_voi_retry.return_value = AIResponse(
        text=json.dumps({
            "chu_de": "T\u1eed Vi T\u1ed5ng Quan",
            "noi_dung": "Cung M\u1ec7nh c\xf3 sao T\u1eed Vi v\u01b0\u1ee3ng \u0111\u1ecba ph\xfa qu\xfd.",
            "muc_do_tin_cay": 0.95
        }),
        provider="mock_gemini",
        tokens_used=200,
        thoi_gian_xu_ly_ms=250,
        thanh_cong=True
    )

    data_input = {
        "reference_id": ref_id,
        "la_tong_quan": True,
        "he_thong": "tu_vi",
        "sao_chu_dao": "T\u1eed Vi"
    }

    with patch("interpretation_api.orchestrator.main_flow.xac_dinh_he_thong", return_value={"he_thong": "tu_vi", "can_hoi_lai": False, "chua_co_du_lieu": False}):
        with patch("interpretation_api.orchestrator.main_flow.search", return_value=[]):
            # L\u1ea7n 1: G\u1ecdi AI v\xe0 l\u01b0u cache
            res1 = luan_giai(
                user_id=str(uid),
                cau_hoi="Lu\u1eadn gi\u1ea3i t\u1ed5ng quan l\xe1 s\u1ed1",
                du_lieu_dau_vao=data_input,
                db=session,
                ai_client=mock_ai
            )
            assert res1["thanh_cong"] is True
            assert mock_ai.goi_ai_voi_retry.call_count == 1
            assert res1.get("tu_cache") is not True

            # L\u1ea7n 2: C\xf9ng l\xe1 s\u1ed1, ph\u1ea3i tr\u1ea3 v\u1ec1 t\u1eeb cache, KH\xd4NG g\u1ecdi AI
            res2 = luan_giai(
                user_id=str(uid),
                cau_hoi="Lu\u1eadn gi\u1ea3i t\u1ed5ng quan l\xe1 s\u1ed1",
                du_lieu_dau_vao=data_input,
                db=session,
                ai_client=mock_ai
            )
            assert res2["thanh_cong"] is True
            assert res2.get("tu_cache") is True
            # Call count c\u1ee7a AI v\u1eabn nguy\xean l\xe0 1
            assert mock_ai.goi_ai_voi_retry.call_count == 1


def test_7_cache_het_han_chay_lai_luong_ai(test_db):
    session, _, uid = test_db
    ref_id = "laso_expired_01"
    key = tao_cache_key("tu_vi", ref_id, cau_hoi=None)

    # T\u1ea1o cache \u0111\xe3 h\u1ebft h\u1ea1n t\u1eeb 2 ng\xe0y tr\u01b0\u1edbc
    expired_entry = InterpretationCache(
        id=uuid.uuid4(),
        he_thong="tu_vi",
        cache_key=key,
        ket_qua_json={"thanh_cong": True, "cau_tra_loi": {"noi_dung": "C\u0169"}},
        tao_luc=datetime.utcnow() - timedelta(days=9),
        het_han_luc=datetime.utcnow() - timedelta(days=2)
    )
    session.add(expired_entry)
    session.commit()

    # Th\u1eed l\u1ea5y cache
    cached = lay_ket_qua_cache(key, db=session)
    assert cached is None  # B\u1ecb b\u1ecf qua v\xec qu\xe1 h\u1ea1n TTL


def test_8_xoa_cache_theo_he_thong(test_db):
    session, _, _ = test_db
    luu_ket_qua_cache("tu_vi_key1", "tu_vi", {"msg": "TV"}, session)
    luu_ket_qua_cache("bat_tu_key1", "bat_tu", {"msg": "BT"}, session)

    # X\xf3a to\xe0n b\u1ed9 cache T\u1eed Vi
    deleted = xoa_cache_theo_he_thong("tu_vi", session)
    assert deleted >= 1

    # T\u1eed Vi kh\xf4ng c\xf2n, nh\u01b0ng B\xe1t T\u1ef1 v\u1eabn c\xf2n nguy\xean
    assert lay_ket_qua_cache("tu_vi_key1", session) is None
    assert lay_ket_qua_cache("bat_tu_key1", session) is not None


def test_9_cau_hoi_chat_tu_do_khong_dung_cache(test_db):
    session, _, uid = test_db
    ref_id = "laso_chat_free_01"
    
    mock_ai = MagicMock()
    mock_ai.goi_ai_voi_retry.return_value = AIResponse(
        text=json.dumps({
            "chu_de": "H\u1ecfi \u0111\xe1p",
            "noi_dung": "N\u0103m nay n\xean h\u1ecdc th\xeam k\u1ef9 n\u0103ng m\u1edbi.",
            "muc_do_tin_cay": 0.9
        }),
        provider="mock_gemini",
        tokens_used=100,
        thoi_gian_xu_ly_ms=150,
        thanh_cong=True
    )

    data_input = {
        "reference_id": ref_id,
        "la_tong_quan": False,  # Chat t\u1ef1 do
        "he_thong": "tu_vi"
    }

    with patch("interpretation_api.orchestrator.main_flow.xac_dinh_he_thong", return_value={"he_thong": "tu_vi", "can_hoi_lai": False, "chua_co_du_lieu": False}):
        with patch("interpretation_api.orchestrator.main_flow.search", return_value=[]):
            # L\u1ea7n 1
            luan_giai(str(uid), "N\u0103m nay l\xe0m g\xec?", data_input, db=session, ai_client=mock_ai)
            # L\u1ea7n 2: Chat t\u1ef1 do ph\u1ea3i g\u1ecdi AI l\u1ea1i
            luan_giai(str(uid), "N\u0103m nay l\xe0m g\xec?", data_input, db=session, ai_client=mock_ai)

    # AI \u0111\u01b0\u1ee3c g\u1ecdi c\u1ea3 2 l\u1ea7n (kh\xf4ng d\xf9ng cache)
    assert mock_ai.goi_ai_voi_retry.call_count == 2


def test_10_tich_hop_thu_tu_cache_quota_ai(test_db):
    session, _, uid = test_db
    ref_id = "laso_order_check_01"
    
    mock_ai = MagicMock()
    mock_ai.goi_ai_voi_retry.return_value = AIResponse(
        text=json.dumps({"chu_de": "T\u1eed Vi", "noi_dung": "Th\xe0nh c\xf4ng", "muc_do_tin_cay": 0.9}),
        provider="mock_gemini",
        tokens_used=100,
        thoi_gian_xu_ly_ms=100,
        thanh_cong=True
    )

    data_input = {
        "reference_id": ref_id,
        "la_tong_quan": True,
        "he_thong": "tu_vi"
    }

    # H\u1ebft quota ngay t\u1eeb \u0111\u1ea7u
    with patch("middleware.quota_service.settings.ai_daily_quota_free_user", 0):
        with patch("interpretation_api.orchestrator.main_flow.xac_dinh_he_thong", return_value={"he_thong": "tu_vi", "can_hoi_lai": False, "chua_co_du_lieu": False}):
            with patch("interpretation_api.orchestrator.main_flow.search", return_value=[]):
                res_blocked = luan_giai(str(uid), "Lu\u1eadn gi\u1ea3i", data_input, db=session, ai_client=mock_ai)
                assert res_blocked["thanh_cong"] is False
                assert res_blocked.get("het_quota") is True
                assert mock_ai.goi_ai_voi_retry.call_count == 0  # Ch\u1eb7n tr\u01b0\u1edbc khi g\u1ecdi AI
