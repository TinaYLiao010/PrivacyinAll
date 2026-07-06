import os
import json
# 获取脚本绝对路径
base_path = os.path.abspath(os.path.dirname(__file__))
# 目录配置
DATA_DIR = os.path.join(base_path, "../poc_sample_datasets")
HTML_OUT_DIR = os.path.join(base_path, "../poc_visual_demos")
# 兼容低版本Python：不使用exist_ok，手动判断再创建
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(HTML_OUT_DIR):
    os.makedirs(HTML_OUT_DIR)
# 文件路径
json_file = os.path.join(DATA_DIR, "poc_sample_law_dataset.json")
output_html = os.path.join(HTML_OUT_DIR, "PoC_Dimension_Classification_Table.html")
# 8个标准维度
DIM_LIST = [
    "BasicDefinition",
    "DataSubjectRight",
    "DataControllerObligation",
    "AutomatedDecision",
    "MinorProtection",
    "CrossBorderTransfer",
    "Penalty",
    "ComplianceAssessment"
]
# 读取数据集
def load_dataset():
    if not os.path.exists(json_file):
        print(f"【错误】不存在 {json_file}，请先执行 poc_struct_generator.py")
        exit(1)
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 新增调试：打印每条法域+条款，确认Python完整读取
    print("\n=== 调试：Python实际读取到的所有法条 ===")
    for idx, item in enumerate(data):
        print(f"{idx+1} | {item['law_code']} | {item['clause_no']} | {item['dimension']}")
    print("=======================================\n")
    return data
# 下拉选项HTML
def build_options():
    opt = '<option value="all">All Dimensions (Show All)</option>\n'
    for d in DIM_LIST:
        opt += f'        <option value="{d}">{d}</option>\n'
    return opt
# 彻底修复JSON多层转义，杜绝截断/解析失败
def safe_json_dump(data):
    # 标准序列化，严格多层转义换行、引号、反斜杠
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    raw = raw.replace("\\", "\\\\")
    raw = raw.replace("\n", "\\n")
    raw = raw.replace("\r", "\\r")
    raw = raw.replace("'", "\\'")
    raw = raw.replace('"', '\\"')
    return raw

if __name__ == "__main__":
    dataset = load_dataset()
    total = len(dataset)
    print(f"✅ Python实际读取法条总数：{total}")
    if total == 0:
        print("⚠️ json为空，表格会空白，请重新运行步骤3 poc_struct_generator.py")
    option_html = build_options()
    js_str = safe_json_dump(dataset)
    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PoC Dimension Classification Table | Bilingual</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:Arial;padding:24px;background:#f3f6f9;}
h1{text-align:center;color:#b91c1c;margin-bottom:10px;}
.desc{text-align:center;color:#555;margin-bottom:24px;font-size:14px;}
.filter-bar{background:#fff;padding:16px;border-radius:8px;margin-bottom:20px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;}
#dimSelect{width:320px;padding:8px;font-size:14px;border:1px solid #ddd;border-radius:6px;}
#keywordInput{width:360px;padding:8px;font-size:14px;border:1px solid #ddd;border-radius:6px;}
#searchBtn{background:#dc2626;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;}
#exportBtn{background:#991b1b;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;}
thead tr{background:#b91c1c;color:#fff;}
th,td{padding:12px 14px;border:1px solid #e2e8f0;text-align:left;font-size:14px;vertical-align:top;}
.col-code{width:8%;}
.col-clause{width:10%;}
.col-dim{width:12%;}
.col-original{width:35%;}
.col-en{width:35%;}
tr:hover{background:#fff1f1;}
.empty-tip{padding:40px;text-align:center;color:#888;font-size:15px;}
.highlight{background:#fff399;padding:0 2px;}
</style>
</head>
<body>
<h1>PoC Law Clause Dimension Classification Table (Bilingual)</h1>
<div class="desc">Source: poc_sample_law_dataset.json | Original Text + Official English Interpretation</div>
<div class="filter-bar">
<label>Filter Dimension:</label>
<select id="dimSelect">
{{OPTION_HTML}}
</select>
<label>Search Keyword:</label>
<input id="keywordInput" placeholder="Match both original & english text">
<button id="searchBtn">Search</button>
<button id="exportBtn">Export All Bilingual Text</button>
</div>
<table>
<thead>
<tr>
<th class="col-code">Law Code</th>
<th class="col-clause">Clause ID</th>
<th class="col-dim">Dimension Tag</th>
<th class="col-original">Original Text</th>
<th class="col-en">Official English Interpretation</th>
</tr>
</thead>
<tbody id="tableBody"></tbody>
</table>

<script>
const fullDataset = JSON.parse('{{JS_DATA}}');
console.log("前端JS读取总条数：", fullDataset.length); // 前端打印条数用于核对
const tableBody = document.getElementById('tableBody');
const selector = document.getElementById('dimSelect');
const keywordInput = document.getElementById('keywordInput');
const searchBtn = document.getElementById('searchBtn');
const exportBtn = document.getElementById('exportBtn');

// 渲染表格：维度筛选 + 关键词双语高亮
function render(){
    const filterDim = selector.value;
    const kw = keywordInput.value.trim().toLowerCase();
    tableBody.innerHTML = "";
    let list = [...fullDataset];
    // 维度过滤
    if(filterDim !== "all"){
        list = list.filter(item => item.dimension === filterDim);
    }
    // 关键词同时匹配原文、英文释义
    if(kw){
        list = list.filter(item=>{
            const ori = item.content_original.toLowerCase();
            const en = item.content_en.toLowerCase();
            return ori.includes(kw) || en.includes(kw);
        })
    }
    // 无匹配提示
    if(list.length === 0){
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = 5;
        td.className = "empty-tip";
        td.innerText = "No matching bilingual clauses found, adjust dimension or keyword.";
        tr.appendChild(td);
        tableBody.appendChild(tr);
        return;
    }
    // 逐行渲染双语两列
    list.forEach(item=>{
        let oriText = item.content_original.replaceAll("\\n", "<br>");
        let enText = item.content_en.replaceAll("\\n", "<br>");
        // 关键词高亮
        if(kw){
            const reg = new RegExp(`(${kw})`, "gi");
            oriText = oriText.replace(reg, `<span class="highlight">$1</span>`);
            enText = enText.replace(reg, `<span class="highlight">$1</span>`);
        }
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${item.law_code}</td>
            <td>${item.clause_no}</td>
            <td>${item.dimension}</td>
            <td style="white-space:pre-line;">${oriText}</td>
            <td class="col-en" style="white-space:pre-line;color:#111;">${enText}</td>
        `;
        tableBody.appendChild(tr);
    })
}

// 导出全部双语文本到剪贴板
function exportAllBilingual(){
    let out = "==== Full Bilingual Law Dataset Export ====\\n\\n";
    fullDataset.forEach(item=>{
        out += `[${item.law_code}] ${item.clause_no} | ${item.dimension}\\nOriginal: ${item.content_original}\\nEnglish: ${item.content_en}\\n\\n`;
    })
    navigator.clipboard.writeText(out).then(()=>alert("All bilingual clauses copied to clipboard!"));
}

// 绑定事件
selector.onchange = render;
searchBtn.onclick = render;
keywordInput.addEventListener("keydown", e=>{if(e.key === "Enter") render();})
exportBtn.onclick = exportAllBilingual;

// 页面初始加载全部数据
render();
</script>
</body>
</html>
'''
    final_html = html_template.replace("{{OPTION_HTML}}", option_html)
    final_html = final_html.replace("{{JS_DATA}}", js_str)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ 双语维度表格页面生成成功：{output_html}")
    print("调试说明：")
    print("1. 运行脚本控制台会打印Python读取的每一条法条清单，核对是否缺失")
    print("2. HTML页面F12控制台会打印前端JS解析到的总条数")
    print("3. 英文列文字已修复为黑色，无暗红色bug")