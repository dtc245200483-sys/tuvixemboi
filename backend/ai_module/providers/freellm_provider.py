# -*- coding: utf-8 -*-
"""
Cổng kết nối AI FreeLLMAPI (FreeLLM Provider).
Tự động tích hợp kho khóa API và endpoint từ D:\\AI github\\freellmapi:
- Tự động giải mã và nạp danh sách Provider Keys (Groq, Cerebras, Mistral, Nvidia) từ freeapi.db.
- Tự động luân chuyển Key (Round-robin / Key rotation) khi một key gặp giới hạn 429.
- Hỗ trợ mô hình ngôn ngữ cao cấp qwen/qwen3.8-27b và openai-compatible format.
- Bảo mật thông tin: Không log key rõ ràng ra ngoài, che dấu (mask) thông tin nhạy cảm.
"""

import os
import time
import sqlite3
import binascii
import logging
import threading
from typing import Optional, List, Dict, Any
import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import settings
from ai_module.base_provider import BaseAIProvider
from ai_module.schemas import AIRequest, AIResponse

logger = logging.getLogger("FreeLLMProvider")

# Đường dẫn mặc định đến cơ sở dữ liệu FreeLLMAPI
DEFAULT_FREELLM_DB = r"D:\AI github\freellmapi\server\data\freeapi.db"
DEFAULT_ENCRYPTION_KEY = "2ac1f647a1367841a052fa585f31800b66189d3af5a48e0befd7301a9265da48"


def _load_keys_from_freellm_db(
    db_path: Optional[str] = None,
    enc_hex: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Tự động đọc và giải mã toàn bộ API Keys sẵn có trong database FreeLLMAPI."""
    resolved_db = db_path or getattr(settings, "freellm_db_path", DEFAULT_FREELLM_DB)
    resolved_key = enc_hex or getattr(settings, "freellm_encryption_key", DEFAULT_ENCRYPTION_KEY)

    if not resolved_db or not os.path.exists(resolved_db):
        logger.warning(f"[FreeLLMProvider] Không tìm thấy file database tại: {resolved_db}")
        return []

    keys = []
    try:
        key_bytes = binascii.unhexlify(resolved_key)
        aesgcm = AESGCM(key_bytes)

        conn = sqlite3.connect(resolved_db)
        cursor = conn.cursor()
        cursor.execute("SELECT id, platform, encrypted_key, iv, auth_tag FROM api_keys WHERE enabled = 1")
        rows = cursor.fetchall()
        conn.close()

        for row_id, platform, enc, iv, tag in rows:
            try:
                ciphertext = binascii.unhexlify(enc) + binascii.unhexlify(tag)
                nonce = binascii.unhexlify(iv)
                decrypted_key = aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
                keys.append({
                    "id": row_id,
                    "platform": platform,
                    "key": decrypted_key
                })
            except Exception as dec_err:
                logger.debug(f"Không thể giải mã key id {row_id}: {dec_err}")
    except Exception as e:
        logger.warning(f"Lỗi khi nạp keys từ FreeLLMAPI DB ({resolved_db}): {e}")

    return keys


class FreeLLMProvider(BaseAIProvider):
    """Provider AI kết nối qua kho khóa FreeLLMAPI với mô hình OpenAI-compatible (Groq Qwen/Llama)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: str = "https://api.groq.com/openai/v1/chat/completions",
        timeout_seconds: float = 3.5,
        db_path: Optional[str] = None,
        encryption_key: Optional[str] = None
    ):
        self.model = model or getattr(settings, "freellm_model", "openai/gpt-oss-120b")
        self.fallback_model = "openai/gpt-oss-20b"
        self.base_url = base_url
        self.timeout = 15.0 if timeout_seconds == 3.5 else timeout_seconds
        self.db_path = db_path or getattr(settings, "freellm_db_path", DEFAULT_FREELLM_DB)
        self.encryption_key = encryption_key or getattr(settings, "freellm_encryption_key", DEFAULT_ENCRYPTION_KEY)
        self._explicit_key = api_key or getattr(settings, "ai_api_key", None)
        self._keys_pool: List[str] = []
        self._current_key_idx = 0
        self._lock = threading.Lock()

        self._refresh_keys_pool()

    @staticmethod
    def _mask_key(key: str) -> str:
        """Che bớt ký tự của key để bảo mật khi ghi log."""
        if not key or len(key) < 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"

    def _refresh_keys_pool(self):
        """Làm mới danh sách API keys từ database và cấu hình."""
        pool: List[str] = []

        # 1. Nạp khóa tường minh từ settings hoặc tham số khởi tạo nếu có
        if self._explicit_key and self._explicit_key.strip():
            pool.append(self._explicit_key.strip())

        # 2. Nạp toàn bộ khóa Groq từ database FreeLLMAPI
        db_keys = _load_keys_from_freellm_db(self.db_path, self.encryption_key)
        for k in db_keys:
            if k.get("platform") == "groq" and k.get("key") and k["key"] not in pool:
                pool.append(k["key"])

        self._keys_pool = pool
        if self._keys_pool:
            logger.info(f"[FreeLLMProvider] Đã nạp thành công {len(self._keys_pool)} keys hoạt động từ FreeLLMAPI.")
        else:
            logger.warning(f"[FreeLLMProvider] Không tìm thấy API key nào trong FreeLLMAPI ({self.db_path}).")

    @property
    def provider_name(self) -> str:
        return "freellmapi"

    def _get_next_key(self) -> Optional[str]:
        """Lấy key tiếp theo trong pool theo cơ chế round-robin (thread-safe)."""
        with self._lock:
            if not self._keys_pool:
                self._refresh_keys_pool()
            if not self._keys_pool:
                return None
            key = self._keys_pool[self._current_key_idx % len(self._keys_pool)]
            self._current_key_idx = (self._current_key_idx + 1) % len(self._keys_pool)
            return key

    def _execute_groq_call(self, api_key: str, payload: dict, t_start: float) -> Optional[AIResponse]:
        """Thực hiện một cuộc gọi HTTP tới Groq API."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.base_url, json=payload, headers=headers)

        elapsed_ms = int((time.perf_counter() - t_start) * 1000)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                return None
            content = choices[0].get("message", {}).get("content", "")
            if not content or not str(content).strip():
                logger.warning(f"[FreeLLMProvider] Groq trả về 200 nhưng content rỗng (finish_reason={choices[0].get('finish_reason')}). Thử key hoặc model khác...")
                return None
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            finish_reason = choices[0].get("finish_reason", "")
            return AIResponse(
                text=content,
                provider=self.provider_name,
                tokens_used=tokens_used,
                thoi_gian_xu_ly_ms=elapsed_ms,
                thanh_cong=True,
                loi_neu_co=None,
                bi_cat_ngang=(finish_reason == "length")
            )
        elif resp.status_code == 429:
            return None
        return None

    def goi_ai(self, request: AIRequest) -> AIResponse:
        """Gửi prompt đến AI với cơ chế tự động luân chuyển Key và fallback model khi gặp 429."""
        t_start = time.perf_counter()

        if not self._keys_pool:
            return AIResponse(
                text="",
                provider=self.provider_name,
                tokens_used=0,
                thoi_gian_xu_ly_ms=int((time.perf_counter() - t_start) * 1000),
                thanh_cong=False,
                loi_neu_co="Hệ thống AI đang bận. Quý bạn vui lòng nhấn lại để thử lại.",
                bi_cat_ngang=False
            )

        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        # Giới hạn max_tokens an toàn theo từng model
        if "qwen" in str(self.model).lower():
            safe_max_tokens = min(request.max_tokens or 600, 650)
        else:
            safe_max_tokens = min(request.max_tokens or 2500, 3500)

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": safe_max_tokens,
            "temperature": request.temperature or 0.7
        }

        # 1. Thử qua tối đa 2 key với model chính
        max_attempts = min(len(self._keys_pool), 2)
        for attempt_i in range(max_attempts):
            api_key = self._get_next_key()
            if not api_key:
                break
            try:
                ai_res = self._execute_groq_call(api_key, payload, t_start)
                if ai_res:
                    return ai_res
                logger.warning(f"[FreeLLMProvider] Key {self._mask_key(api_key)} gặp giới hạn hoặc lỗi, thử key kế tiếp...")
            except Exception as ex:
                logger.debug(f"[FreeLLMProvider] Ngoại lệ khi gọi {self._mask_key(api_key)}: {ex}")

        # 2. Nếu model chính gặp 429 trên các key, tự động chuyển sang fallback model (hạn mức 70.000 tokens)
        logger.info(f"[FreeLLMProvider] Kích hoạt fallback sang mô hình '{self.fallback_model}'...")
        payload_fallback = dict(payload)
        payload_fallback["model"] = self.fallback_model

        for fallback_i in range(min(len(self._keys_pool), 2)):
            api_key = self._get_next_key()
            if not api_key:
                break
            try:
                ai_res = self._execute_groq_call(api_key, payload_fallback, t_start)
                if ai_res:
                    return ai_res
            except Exception as ex:
                logger.debug(f"[FreeLLMProvider] Fallback key {self._mask_key(api_key)} lỗi: {ex}")

        elapsed_ms = int((time.perf_counter() - t_start) * 1000)
        return AIResponse(
            text="",
            provider=self.provider_name,
            tokens_used=0,
            thoi_gian_xu_ly_ms=elapsed_ms,
            thanh_cong=False,
            loi_neu_co="Hệ thống AI đang bận kết nối. Quý bạn vui lòng nhấn lại để tiếp tục.",
            bi_cat_ngang=False
        )

