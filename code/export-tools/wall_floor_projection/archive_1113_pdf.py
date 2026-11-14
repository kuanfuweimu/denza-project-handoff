import sys
sys.path.insert(0, r"C:\Users\kuanf\.gemini\antigravity\brain\c31a3e71-6598-4524-86ea-b6b6f44cd294\scratch\pylibs")
import os
import shutil
import json
import hashlib
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

src_pdf = r"D:\WeChat\xwechat_files\wxid_y5xcvbymgrea12_81c2\msg\file\2026-11\c0bd31e50ce7c7c6b469852e6522720b.pdf"
dst_denza_n = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\1113_Z_dance_concept_breakdown.pdf"
dst_client_dir = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA 2\2026-11_DENZA Z\00_项目资料\客户方案"
dst_client_pdf = os.path.join(dst_client_dir, "1113_Z_dance_concept_breakdown.pdf")
preview_dir = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA 2\2026-11_DENZA Z\00_项目资料\舞蹈分镜拆解_1113"

os.makedirs(dst_client_dir, exist_ok=True)
os.makedirs(preview_dir, exist_ok=True)

if not os.path.exists(dst_denza_n):
    shutil.copy2(src_pdf, dst_denza_n)
if not os.path.exists(dst_client_pdf):
    shutil.copy2(src_pdf, dst_client_pdf)

with open(src_pdf, "rb") as f:
    sha256_hash = hashlib.sha256(f.read()).hexdigest()

doc = fitz.open(src_pdf)
pages_data = []
text_lines = []
page_pngs = []

for i, page in enumerate(doc):
    pno = i + 1
    txt = page.get_text("text").strip()
    pages_data.append({"page": pno, "text": txt})
    text_lines.append(f"=== Page {pno:02d} ===\n{txt}")
    # Render 1920x1080 PNG
    scale = 1920.0 / max(page.rect.width, 1.0)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    png_path = os.path.join(preview_dir, f"page-{pno:02d}.png")
    img.save(png_path)
    page_pngs.append(png_path)

with open(os.path.join(preview_dir, "pages.json"), "w", encoding="utf-8") as f:
    json.dump(pages_data, f, ensure_ascii=False, indent=2)

with open(os.path.join(preview_dir, "dance_concept_text.txt"), "w", encoding="utf-8") as f:
    f.write("\n\n".join(text_lines))

# Build contact sheets (4 cols x 3 rows = 12 pages per sheet, matching contact-1.jpg style)
font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
cols, rows = 4, 3
per_sheet = 12
thumb_w, thumb_h = 640, 360
pad_x, pad_y, top_label = 24, 24, 34

for s_idx in range(0, len(page_pngs), per_sheet):
    batch = page_pngs[s_idx:s_idx + per_sheet]
    r_count = (len(batch) + cols - 1) // cols
    sheet_w = cols * thumb_w + (cols + 1) * pad_x
    sheet_h = r_count * (thumb_h + top_label) + (r_count + 1) * pad_y
    sheet = Image.new("RGB", (sheet_w, sheet_h), (218, 218, 218))
    dr = ImageDraw.Draw(sheet)
    for j, p_path in enumerate(batch):
        pno = s_idx + j + 1
        r = j // cols
        c = j % cols
        x0 = pad_x + c * (thumb_w + pad_x)
        y0 = pad_y + r * (thumb_h + top_label + pad_y)
        dr.text((x0, y0), f"page-{pno:02d}", fill=(30, 30, 30), font=font)
        im = Image.open(p_path).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(im, (x0, y0 + top_label))
    c_path = os.path.join(preview_dir, f"contact-{s_idx // per_sheet + 1}.jpg")
    sheet.save(c_path, quality=88)

print("Archived PDF and 21 page previews. SHA256:", sha256_hash)
