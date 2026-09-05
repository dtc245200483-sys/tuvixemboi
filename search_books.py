# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

folder = 'd:/ung dung tri tue nhan ao/tuvixemboi/Data_training/extracted_text/tu_vi'
for f in os.listdir(folder):
    if f.endswith('.txt'):
        path = os.path.join(folder, f)
        with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
            found = []
            for query in ['cục', 'ngũ hổ độn', 'định cục', 'an mệnh', 'huynh đệ', 'phụ mẫu']:
                cnt = content.lower().count(query)
                if cnt > 0:
                    found.append(f"'{query}': {cnt}")
            if found:
                print(f"{f} -> {', '.join(found)}")
