# -*- coding: utf-8 -*-
import importlib

from astro_engine.kinh_dich.constants.bat_quai import (
    BAT_QUAI,
    BAT_QUAI_BY_NAME,
    BAT_QUAI_BY_CODE
)

# Import module 64_que dynamically
_mod = importlib.import_module(".64_que", package="astro_engine.kinh_dich.constants")
QUE_64 = _mod.QUE_64
QUE_BY_CODE = _mod.QUE_BY_CODE
QUE_BY_STT = _mod.QUE_BY_STT
