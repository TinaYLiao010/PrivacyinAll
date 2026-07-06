import os

# 自动定位数据集文件夹，无需手动切换路径
base_path = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(base_path, "../poc_sample_datasets")
# 自动创建文件夹（不存在则生成，解决路径报错）
os.makedirs(INPUT_DIR, exist_ok=True)

def clean_text(raw_content):
    """清洗文本：去除空行、首尾多余空格"""
    lines = raw.splitlines()
    clean_lines = []
    for line in lines:
        strip_line = line.strip()
        if not strip_line:
            continue
        clean_lines.append(strip_line)
    return "\n".join(clean_lines)

if __name__ == "__main__":
    file_list = os.listdir(INPUT_DIR)
    # 处理raw txt文件，生成PoC归档MD
    for fname in file_list:
        if fname.endswith("_raw.txt"):
            code = fname.replace("_raw.txt", "")
            raw_path = os.path.join(INPUT_DIR, fname)
            out_md_name = f"{code}_PoC_Archive.md"
            out_md = os.path.join(INPUT_DIR, out_md_name)
            with open(raw_path, "r", encoding="utf-8") as f:
                raw = f.read()
            clean_content = clean_text(raw)
            # 写入标准化归档MD
            with open(out_md, "w", encoding="utf-8") as f:
                f.write(f"# {code} PoC Clean Archive\n\n{clean_content}")
            print(f"✅ 生成归档文件：{out_md_name}")
    # 检测韩国MD是否存在，无需重复生成
    kr_md_path = os.path.join(INPUT_DIR, "KR_PIPA_PoC_Archive.md")
    if os.path.exists(kr_md_path):
        print("✅ KR_PIPA_PoC_Archive.md 已存在，跳过清洗步骤")
    else:
        print("⚠️ 警告：未找到KR_PIPA_PoC_Archive.md，请检查文件存放位置")
    print("\n===== 文本清洗流程执行完成 =====")