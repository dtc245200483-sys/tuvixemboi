# -*- coding: utf-8 -*-
import sys
import urllib.request
import urllib.parse
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:8000'

def request(method, path, body=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f'{BASE}{path}', data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

email = 'live_test_user_2026@khaitamhuyenhoc.vn'
pwd = 'Password123@'
status, resp = request('POST', '/auth/register', {'email': email, 'password': pwd, 'confirm_password': pwd})

login_data = urllib.parse.urlencode({'username': email, 'password': pwd}).encode()
login_req = urllib.request.Request(f'{BASE}/auth/login', data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, method='POST')
with urllib.request.urlopen(login_req) as r:
    token = json.loads(r.read().decode())['access_token']

print('1. Logged in successfully. Token obtained.')

# 2. Check initial Quota
status, q0 = request('GET', '/quota', token=token)
print('2. Initial Quota:', q0['du_lieu'])

# 3. Create Main Profile (Pham Vu Quang Hung)
status, p_main = request('POST', '/birth-profile', {
    'ho_ten': 'Phạm Vũ Quang Hưng',
    'ngay_sinh_duong': '1888-05-29',
    'gio_sinh': 4,
    'phut_sinh': 0,
    'gioi_tinh': 'nam'
}, token=token)
main_id = p_main['du_lieu']['id']
print('3. Created Main Profile:', p_main['du_lieu']['ho_ten'], '| is_default:', p_main['du_lieu']['is_default'])

# 4. Perform An Sao Lap La So (Nguyen Van B) via /birth-profile/an-sao
status, p_ansao = request('POST', '/birth-profile/an-sao', {
    'ho_ten': 'Nguyễn Văn B (Nhập tại An Sao Nhanh)',
    'ngay_sinh_duong': '2001-02-03',
    'gio_sinh': 8,
    'phut_sinh': 15,
    'gioi_tinh': 'nu'
}, token=token)
print('4. An Sao Profile created:', p_ansao['du_lieu']['ho_ten'], '| is_default:', p_ansao['du_lieu']['is_default'], '| is_quick_chart:', p_ansao['du_lieu']['is_quick_chart'])

# 5. Check Quota deducted by 1
status, q1 = request('GET', '/quota', token=token)
print('5. Quota after 1 An Sao: used=', q1['du_lieu']['so_luot_da_dung'], 'remaining=', q1['du_lieu']['so_luot_con_lai'], 'countdown=', q1['du_lieu']['so_giay_con_lai_den_reset'])
assert q1['du_lieu']['so_luot_da_dung'] == 1

# 6. Check list of profiles: Main Profile must still be at index 0 because is_default=True
status, plist = request('GET', '/birth-profile', token=token)
top_profile = plist['du_lieu'][0]
print('6. Top profile on Dashboard:', top_profile['ho_ten'], '(id=', top_profile['id'], ', is_default=', top_profile['is_default'], ')')
assert top_profile['id'] == main_id
assert top_profile['ho_ten'] == 'Phạm Vũ Quang Hưng'
print('>>> VERIFIED: An Sao Lap La So did NOT alter or replace Ho So Menh Dang Chon!')

# 7. Upgrade to Premium
status, upg = request('POST', '/quota/upgrade-premium', token=token)
print('7. Upgrade Premium:', upg['du_lieu']['thong_bao'])

# 8. Check Quota after Premium
status, q_prem = request('GET', '/quota', token=token)
print('8. Quota as Premium VIP: is_premium=', q_prem['du_lieu']['is_premium'], 'remaining=', q_prem['du_lieu']['so_luot_con_lai'])
assert q_prem['du_lieu']['is_premium'] is True
assert q_prem['du_lieu']['so_luot_con_lai'] == 999999

# 9. An sao again as Premium: succeeds without deducting or blocking
status, p_ansao2 = request('POST', '/birth-profile/an-sao', {
    'ho_ten': 'Người xem VIP Premium',
    'ngay_sinh_duong': '1990-10-10',
    'gio_sinh': 12,
    'phut_sinh': 0,
    'gioi_tinh': 'nam'
}, token=token)
print('9. Premium An Sao status:', status, '|', p_ansao2['du_lieu']['ho_ten'])
assert status == 201
print('>>> ALL LIVE E2E CHECKS PASSED PERFECTLY!')
