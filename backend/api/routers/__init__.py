# -*- coding: utf-8 -*-
from .birth_profile_router import router as birth_profile_router
from .tu_vi_router import router as tu_vi_router
from .bat_tu_router import router as bat_tu_router
from .kinh_dich_router import router as kinh_dich_router
from .nhan_tuong_router import router as nhan_tuong_router
from .chat_router import router as chat_router
from .quota_router import router as quota_router

__all__ = [
    "birth_profile_router",
    "tu_vi_router",
    "bat_tu_router",
    "kinh_dich_router",
    "nhan_tuong_router",
    "chat_router",
    "quota_router",
]
