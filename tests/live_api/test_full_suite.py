import sys
import json
import urllib.request
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:8000'

def p(msg):
    print(msg, flush=True)

def run_tests():
    p("==================================================")
    p("   KIỂM TRA TOÀN DIỆN HỆ THỐNG API BACKEND")
    p("==================================================")
    
    # 1. Health Check
    try:
        res = urllib.request.urlopen(f'{BASE}/health', timeout=10)
        health = json.loads(res.read().decode('utf-8'))
        p(f"[✓] 1. GET /health: Thành công -> {health}")
    except Exception as e:
        p(f"[X] 1. GET /health thất bại: {e}")
        return

    # 2. Login
    try:
        login_data = urllib.parse.urlencode({
            'username': 'admin@khaitamhuyenhoc.com',
            'password': 'Admin@123456'
        }).encode()
        req = urllib.request.Request(
            f'{BASE}/auth/login',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        res = urllib.request.urlopen(req, timeout=10)
        tokens = json.loads(res.read().decode('utf-8'))
        token = tokens['access_token']
        p(f"[✓] 2. POST /auth/login: Đăng nhập thành công! Token type: {tokens.get('token_type')}")
    except Exception as e:
        p(f"[X] 2. POST /auth/login thất bại: {e}")
        return

    auth_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # 3. Auth Me
    try:
        req = urllib.request.Request(f'{BASE}/auth/me', headers=auth_headers)
        res = urllib.request.urlopen(req, timeout=10)
        me = json.loads(res.read().decode('utf-8'))
        p(f"[✓] 3. GET /auth/me: Email={me.get('email')}, ID={me.get('id')}")
    except Exception as e:
        p(f"[X] 3. GET /auth/me thất bại: {e}")

    # 4. Quota
    try:
        req = urllib.request.Request(f'{BASE}/quota', headers=auth_headers)
        res = urllib.request.urlopen(req, timeout=10)
        quota = json.loads(res.read().decode('utf-8'))
        p(f"[✓] 4. GET /quota: Hạn mức={quota.get('du_lieu')}")
    except Exception as e:
        p(f"[X] 4. GET /quota thất bại: {e}")

    # 5. Birth Profile
    profile_id = None
    try:
        req = urllib.request.Request(f'{BASE}/birth-profile', headers=auth_headers)
        res = urllib.request.urlopen(req, timeout=10)
        raw_profiles = json.loads(res.read().decode('utf-8'))
        if isinstance(raw_profiles, list):
            profile_list = raw_profiles
        elif isinstance(raw_profiles, dict):
            profile_list = raw_profiles.get('du_lieu', raw_profiles.get('items', [raw_profiles]))
        else:
            profile_list = []
            
        p(f"[✓] 5. GET /birth-profile: Tìm thấy {len(profile_list)} hồ sơ.")
        if profile_list and isinstance(profile_list[0], dict) and 'id' in profile_list[0]:
            profile_id = profile_list[0]['id']
            p(f"    Sử dụng hồ sơ ID: {profile_id} ({profile_list[0].get('ho_ten', '')})")
    except Exception as e:
        p(f"[X] 5. GET /birth-profile thất bại: {e}")

    # 6. Tu Vi
    if profile_id:
        try:
            req = urllib.request.Request(f'{BASE}/tu-vi/{profile_id}', headers=auth_headers)
            res = urllib.request.urlopen(req, timeout=30)
            tuvi = json.loads(res.read().decode('utf-8'))
            data_tuvi = tuvi.get('du_lieu', tuvi)
            la_so = data_tuvi.get('la_so', {})
            p(f"[✓] 6. GET /tu-vi/{profile_id}: Thành công! Bản mệnh={la_so.get('ban_menh', 'OK')}, Cục={la_so.get('cuc', 'OK')}")
        except Exception as e:
            p(f"[X] 6. GET /tu-vi/{profile_id} thất bại: {e}")

    # 7. Bat Tu
    if profile_id:
        try:
            req = urllib.request.Request(f'{BASE}/bat-tu/{profile_id}', headers=auth_headers)
            res = urllib.request.urlopen(req, timeout=30)
            battu = json.loads(res.read().decode('utf-8'))
            data_battu = battu.get('du_lieu', battu)
            tu_tru = data_battu.get('tu_tru', {})
            p(f"[✓] 7. GET /bat-tu/{profile_id}: Thành công! Trụ Năm={tu_tru.get('nam', 'OK')}")
        except Exception as e:
            p(f"[X] 7. GET /bat-tu/{profile_id} thất bại: {e}")

    # 8. Gieo Que (Kinh Dich)
    try:
        que_req = {
            "phuong_phap": "dong_xu",
            "cau_hoi": "Hôm nay công việc hanh thông không?"
        }
        req = urllib.request.Request(f'{BASE}/gieo-que', data=json.dumps(que_req).encode(), headers=auth_headers)
        res = urllib.request.urlopen(req, timeout=30)
        que = json.loads(res.read().decode('utf-8'))
        data_que = que.get('du_lieu', que)
        p(f"[✓] 8. POST /gieo-que: Thành công! Quẻ={data_que.get('que_thuan', {}).get('ten', 'OK')}")
    except Exception as e:
        p(f"[X] 8. POST /gieo-que thất bại: {e}")

    # 9. Chat AI
    try:
        chat_req = {
            "cau_hoi": "Xin chào, bạn có thể giúp gì cho tôi?",
            "he_thong": "tu_vi"
        }
        req = urllib.request.Request(f'{BASE}/chat', data=json.dumps(chat_req).encode(), headers=auth_headers)
        res = urllib.request.urlopen(req, timeout=30)
        chat_res = json.loads(res.read().decode('utf-8'))
        data_chat = chat_res.get('du_lieu', chat_res)
        tra_loi = data_chat.get('tra_loi', str(data_chat))
        p(f"[✓] 9. POST /chat: Thành công! Phản hồi: {tra_loi[:120]}...")
    except Exception as e:
        p(f"[X] 9. POST /chat thất bại: {e}")

    p("==================================================")
    p("       HOÀN TẤT KIỂM TRA TOÀN BỘ API BACKEND      ")
    p("==================================================")

if __name__ == '__main__':
    run_tests()
