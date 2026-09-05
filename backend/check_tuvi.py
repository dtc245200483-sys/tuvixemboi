import sys
sys.stdout.reconfigure(encoding='utf-8')
from astro_engine.tu_vi.core import *

# 1. Kiem tra Dai Van
print("=== 1. DAI VAN ===")
cuc_test = {'so_cuc': 5, 'ten': 'Tho Ngu Cuc'}
dv = tinh_dai_van(cuc_test, 'nam', 1, 'Bính Tuất')  # menh = Suu(1)
print('Dai van Nam Binh Tuat, menh Suu(1), cuc 5:')
for d in dv[:6]:
    cung_str = CUNG_DIA_CHI[d["cung_vi_tri"]]
    print(f'  DV {d["so_thu_tu"]}: cung {cung_str}({d["cung_vi_tri"]}), tuoi {d["giai_doan"]}')

# 2. Kiem tra Loc Ton duoi chuan co thu
print("\n=== 2. LOC TON STANDARD ===")
loc_ton_standard = {
    'Giap': 'Dan',   # idx 2 -- OK
    'At': 'Mao',     # idx 3 -- OK
    'Binh': 'Ty',    # idx 5 -- OK
    'Dinh': 'Ngo',   # idx 6 -- OK
    'Mau': 'Ty',     # idx 5 -- OK 
    'Ky': 'Ngo',     # idx 6 -- OK
    'Canh': 'Than',  # idx 8 -- OK
    'Tan': 'Dau',    # idx 9 -- OK
    'Nham': 'Hoi',   # idx 11 -- OK
    'Quy': 'Ty'      # idx 0 -- OK
}
loc_ton_table = {0: 2, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 11, 9: 0}
for idx, can in enumerate(CAN_LIST):
    pos = loc_ton_table[idx]
    print(f'{can} (idx {idx}): Loc Ton = {CUNG_DIA_CHI[pos]} (idx {pos})')

# 3. Kiem tra Hoa Tinh theo Bang chuan
print("\n=== 3. HOA TINH / LINH TINH STANDARD (ref: Nguyen Phat Loc) ===")
# Bang Hoa Tinh:
# Dan Ngo Tuat: khoi Suu(1), di thuan -> code dung
# Than Ty Thin: khoi Dan(2), di thuan -> code dang dung la 2
#   Nhung mot so sach noi khoi Mao(3)???
# Ty Dau Suu: khoi Mao(3), di thuan -> code dung
# Hoi Mao Mui: khoi Dau(9), di thuan -> code dung

# Bang Linh Tinh:
# Dan Ngo Tuat: khoi Mao(3), di nghich -> code: linh_base=3, linh_dir=-1 -> dung
# Than Ty Thin: khoi Tuat(10), di nghich -> code: linh_base=10, linh_dir=-1 -> dung
# Ty Dau Suu: khoi Tuat(10), di nghich -> code: linh_base=10, linh_dir=-1 -> dung
# Hoi Mao Mui: khoi Tuat(10), di nghich -> code: linh_base=10, linh_dir=-1 -> dung

print("Hoa Tinh starting positions per chi group:")
print("Dan Ngo Tuat (code base=1=Suu): ", end="")
for gio in ['Ty', 'Suu', 'Dan']:
    idx = CHI_TO_IDX[gio]
    pos = (1 + idx) % 12
    print(f"{gio}->{CUNG_DIA_CHI[pos]} ", end="")
print()
print("Than Ty Thin (code base=2=Dan): ", end="")
for gio in ['Ty', 'Suu', 'Dan']:
    idx = CHI_TO_IDX[gio]
    pos = (2 + idx) % 12
    print(f"{gio}->{CUNG_DIA_CHI[pos]} ", end="")
print()

# 4. Kiem tra logic Thien Phu
print("\n=== 4. THIEN PHU STANDARD ===")
print("Theo co thu, TuVi va ThienPhu doi xung qua truc Dan-Than:")
print("TuVi + ThienPhu = 10 (mod 12)? Hay = 4?")
# Neu doi xung qua truc Dan(2)-Than(8), thi:
# TuVi = 2 -> ThienPhu = 2 (dong cung Dan) -- DUNG voi test 3
# TuVi = 8 -> ThienPhu = 8 (dong cung Than) 
# TuVi = 0 (Ty) -> doi xung qua Dan(2): ThienPhu = 4 (Thin)
# TuVi = 1 (Suu) -> ThienPhu = 3 (Mao)
# => ThienPhu = (4 - TuVi) % 12 -- DUNG
for tv in [0, 1, 2, 5, 8, 9, 11]:
    tp_code = (4 - tv) % 12
    print(f"TuVi={CUNG_DIA_CHI[tv]}({tv}) -> ThienPhu(code)={CUNG_DIA_CHI[tp_code]}({tp_code})")

# 5. Kiem tra logic Tuan Khong
print("\n=== 5. TUAN KHONG - TRIET KHONG ===")
# Tuan Khong: 2 dia chi cuoi trong vong 60 hoa giap chua co can
# Chiem theo Can-Chi nam
# Neu Can = 0 (Giap), Chi = 0 (Ty) -> Giap Ty -> Tuan tu Ty den Tuat: Tuan Khong: Tuat(10)+Hoi(11)? 
# Hay: 2 chi ngoai vong tuan
# chi_dau_tuan = (chi_nam_idx - can_nam_idx) % 12
# tuan_pos = [(chi_dau_tuan - 2) % 12, (chi_dau_tuan - 1) % 12]

# Test: Nam Giap Ty (can_idx=0, chi_idx=0)
# chi_dau_tuan = (0 - 0) % 12 = 0 (Ty)
# tuan_pos = [-2%12, -1%12] = [10, 11] = [Tuat, Hoi] -> DUNG (Giap Ty tuan tuan khong la Tuat Hoi)

# Test: Nam Binh Tuat (can_idx=2, chi_idx=10)
# chi_dau_tuan = (10 - 2) % 12 = 8 (Than)
# Tuan Binh Than -> Tu Chi: Than Dau Tuat Hoi Ty Suu Dan Mao Thin Ty -> Khong: Ngo Mui
# tuan_pos = [(8-2)%12, (8-1)%12] = [6, 7] = [Ngo, Mui] -> DUNG!

can_idx = 2  # Binh
chi_idx = 10  # Tuat
chi_dau_tuan = (chi_idx - can_idx) % 12
tuan_pos = [(chi_dau_tuan - 2) % 12, (chi_dau_tuan - 1) % 12]
print(f"Nam Binh Tuat: chi_dau_tuan={CUNG_DIA_CHI[chi_dau_tuan]}, Tuan Khong: {[CUNG_DIA_CHI[p] for p in tuan_pos]}")
# test_case_12 expects: tuan 6,7 (Ngo, Mui) for Binh Tuat -- VERIFIED

# 6. Kiem tra Triet Khong
print("\n=== 6. TRIET KHONG VERIFICATION ===")
# Nam Binh Tuat: can_idx=2 -> triet_table[2] = [4,5] (Thin Ty)
# test_case_12 expects: 4,5 in triet -> DUNG
triet_table = {
    0: [8, 9], 5: [8, 9],   # Giap, Ky: Than - Dau
    1: [6, 7], 6: [6, 7],   # At, Canh: Ngo - Mui
    2: [4, 5], 7: [4, 5],   # Binh, Tan: Thin - Ty
    3: [2, 3], 8: [2, 3],   # Dinh, Nham: Dan - Mao
    4: [0, 1], 9: [0, 1]    # Mau, Quy: Ty - Suu
}
print("Triet Khong by Can nam:")
for can_idx, triet in triet_table.items():
    print(f"  {CAN_LIST[can_idx]}: {[CUNG_DIA_CHI[t] for t in triet]}")

# 7. Kiem tra logic Menh Chu - co sach nao noi khac?
print("\n=== 7. MENH CHU (so sanh voi standard) ===")
# Menh Chu duoc xac dinh theo dia chi cung Menh
from astro_engine.tu_vi.constants.sao import MENH_CHU_MAP
for chi, sao in MENH_CHU_MAP.items():
    print(f"  Cung Menh {chi}: {sao}")

# 8. Kiem tra THAN CHU
print("\n=== 8. THAN CHU (so sanh voi standard) ===")
from astro_engine.tu_vi.constants.sao import THAN_CHU_MAP
for chi, sao in THAN_CHU_MAP.items():
    print(f"  Chi nam {chi}: {sao}")

# Theo co thu: Than Chu theo Chi nam sinh:
# Ty -> Linh Tinh        (code: Linh Tinh) -- DUNG
# Suu -> Thien Tuong     (code: Thien Tuong) -- DUNG
# Dan -> Thien Luong     (code: Thien Luong) -- DUNG
# Mao -> Thien Dong      (code: Thien Dong) -- DUNG
# Thin -> Van Xuong      (code: Van Xuong) -- DUNG
# Ty -> Thien Co         (code: Thien Co) -- DUNG
# Ngo -> Hoa Tinh        (code: Hoa Tinh) -- DUNG
# Mui -> Thien Tuong     (code: Thien Tuong) -- DUNG
# Than -> Thien Luong    (code: Thien Luong) -- DUNG
# Dau -> Thien Dong      (code: Thien Dong) -- DUNG
# Tuat -> Van Xuong      (code: Van Xuong) -- DUNG
# Hoi -> Thien Co        (code: Thien Co) -- DUNG
