import os

base_path = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(base_path, "../poc_sample_datasets")
OUT_HTML_DIR = os.path.join(base_path, "../poc_visual_demos")
OUT_HTML = os.path.join(OUT_HTML_DIR, "PoC_Law_Archive_Preview.html")
os.makedirs(OUT_HTML_DIR, exist_ok=True)

# 读取MD文件工具函数
def read_md(code):
    md_path = os.path.join(INPUT_DIR, f"{code}_PoC_Archive.md")
    if not os.path.exists(md_path):
        return f"【Warning】Missing File: {code}_PoC_Archive.md, please check dataset folder!"
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read()

# 读取三部法规文本
cn_text = read_md("CN_PIPL")
jp_text = read_md("JP_APPI")
kr_text = read_md("KR_PIPA")

# 页面模板：全部标题、说明替换为英文标注，样式不变
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PoC_Law_Archive_Preview | Three Jurisdiction Full Text Side-by-Side Preview</title>
    <style>
        * {box-sizing: border-box;margin:0;padding:0;}
        body {padding:20;font-family: system-ui, sans-serif;background:#f5f7fa;}
        h1 {text-align:center;margin-bottom:24;color:#222;font-size:22px;}
        .sub-desc {
            text-align: center;
            color: #555;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .container {display:grid;grid-template-columns:1fr 1fr 1fr;gap:16;margin-top:10px;}
        .col-card {background:#fff;border-radius:8;padding:16;height:85vh;overflow-y:auto;border:1px solid #e5e7eb;}
        .col-title {font-size:18;font-weight:bold;margin-bottom:12;padding-bottom:8;border-bottom:1px solid #ddd;color:#111;}
        .content-text {white-space:pre-wrap;line-height:1.6;font-size:14;color:#333;}
        .tip-text {
            margin-top: 10px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>PoC Full Legal Archive Side-by-Side Preview</h1>
    <div class="sub-desc">
        Independent vertical scroll for each column | Source File: *_PoC_Archive.md | Static Page (No Server Required)
    </div>
    <div class="container">
        <div class="col-card">
            <div class="col-title">CN-PIPL - Personal Information Protection Law of China</div>
            <div class="tip-text">Raw Source: CN_PIPL_raw.txt | Cleaned Archive</div>
            <div class="content-text">{{CN_CONTENT}}</div>
        </div>
        <div class="col-card">
            <div class="col-title">JP-APPI - Act on the Protection of Personal Information (Japan)</div>
            <div class="tip-text">Raw Source: JP_APPI_raw.txt | Cleaned Archive</div>
            <div class="content-text">{{JP_CONTENT}}</div>
        </div>
        <div class="col-card">
            <div class="col-title">KR-PIPA - Personal Information Protection Act (Republic of Korea)</div>
            <div class="tip-text">Structured Source: KR_PIPA_PoC_Archive.md</div>
            <div class="content-text">{{KR_CONTENT}}</div>
        </div>
    </div>
</body>
</html>
"""

# 填充法规原文
html_content = html_template.replace("{{CN_CONTENT}}", cn_text)\
                            .replace("{{JP_CONTENT}}", jp_text)\
                            .replace("{{KR_CONTENT}}", kr_text)

# 写入HTML文件
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ PoC_Law_Archive_Preview.html generated successfully")
print(f"Output Path: {OUT_HTML}")
print("Page Feature: All titles & descriptions marked in English, 3 independent scroll columns, static offline page")