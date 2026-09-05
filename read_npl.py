# -*- coding: utf-8 -*-
import fitz, io, sys

# Bộ chuyển đổi ký tự VNI sang Unicode
vni_map = {
    'aù': 'á', 'aø': 'à', 'aû': 'ả', 'aõ': 'ã', 'aï': 'ạ',
    'aâ': 'â', 'aás': 'ấ', 'aà': 'ầ', 'aå': 'ẩ', 'aã': 'ẫ', 'aä': 'ậ',
    'aê': 'ă', 'aé': 'ắ', 'aè': 'ằ', 'aú': 'ẳ', 'aü': 'ẵ', 'aë': 'ặ',
    'eù': 'é', 'eø': 'è', 'eû': 'ẻ', 'eõ': 'ẽ', 'eï': 'ẹ',
    'eâ': 'ê', 'eás': 'ế', 'eà': 'ề', 'eå': 'ể', 'eã': 'ễ', 'eä': 'ệ',
    'où': 'ó', 'oø': 'ò', 'oû': 'ỏ', 'oõ': 'õ', 'oï': 'ọ',
    'oâ': 'ô', 'oás': 'ố', 'oà': 'ồ', 'oå': 'ổ', 'oã': 'ỗ', 'oä': 'ộ',
    'ôù': 'ớ', 'ôø': 'ờ', 'ôû': 'ở', 'ôõ': 'ỡ', 'ôï': 'ợ',
    'uù': 'ú', 'uø': 'ù', 'uû': 'ủ', 'uõ': 'ũ', 'uï': 'ụ',
    'öù': 'ứ', 'öø': 'ừ', 'öû': 'ử', 'öõ': 'ữ', 'öï': 'ự', 'ö': 'ư',
    'iù': 'í', 'iø': 'ì', 'iû': 'ỉ', 'iõ': 'ĩ', 'iï': 'ị',
    'yù': 'ý', 'yø': 'ỳ', 'yû': 'ỷ', 'yõ': 'ỹ', 'yï': 'ỵ',
    'ñ': 'đ', 'Ñ': 'Đ',
    'Töû': 'Tử', 'Meänh': 'Mệnh', 'Cuïc': 'Cục'
}

def decode_vni(text):
    for k, v in vni_map.items():
        text = text.replace(k, v)
    return text

doc = fitz.open('d:/ung dung tri tue nhan ao/tuvixemboi/Data_training/raw_sources/tu_vi/tu vi tong hop-nguyen-phat-loc.pdf')
for p in range(21, 35):
    t = doc[p].get_text()
    t_clean = decode_vni(t)
    print(f"=== TRANG {p+1} ===")
    lines = [line for line in t_clean.splitlines() if line.strip()]
    for line in lines[:30]:
        print(line[:120].encode('ascii', 'backslashreplace').decode('ascii'))
