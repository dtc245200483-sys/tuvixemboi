# -*- coding: utf-8 -*-
import sys, io, os
import fitz # PyMuPDF
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf_path = "d:/ung dung tri tue nhan ao/tuvixemboi/Data_training/raw_sources/tu_vi/tu vi tong hop-nguyen-phat-loc.pdf"
doc = fitz.open(pdf_path)
print(f"Loaded {pdf_path}: {len(doc)} pages")

keywords = ["định cục", "ngũ hổ độn", "an mệnh", "an thân", "an tử vi", "12 cung", "hỏa lục cục", "thổ ngũ cục", "cục số", "phụ mẫu", "huynh đệ"]

matches = {kw: [] for kw in keywords}

for page_num in range(len(doc)):
    text = doc[page_num].get_text()
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            matches[kw].append(page_num + 1)

for kw, pgs in matches.items():
    print(f"Keyword '{kw}': found on {len(pgs)} pages -> {pgs[:15]}")
