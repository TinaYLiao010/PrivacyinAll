import os
import json

base_path = os.path.abspath(os.path.dirname(__file__))
DATA_JSON = os.path.join(base_path, "../poc_sample_datasets/poc_sample_law_dataset.json")
HTML_OUT = os.path.join(base_path, "../poc_visual_demos")

# 创建文件夹，兼容无exist_ok旧Python
if not os.path.exists(HTML_OUT):
    os.makedirs(HTML_OUT)

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
JURIS_LIST = ["CN_PIPL", "JP_APPI", "KR_PIPA"]

def load_dataset():
    if not os.path.exists(DATA_JSON):
        print(f"Error: Missing {DATA_JSON}, run PoC Step3 first!")
        exit(1)
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Loaded total bilingual clauses: {len(data)}")
    return data

# 四重转义：反斜杠、单双引号、换行全部转义，杜绝非法token
def safe_encode(raw):
    s = json.dumps(raw, ensure_ascii=False, separators=(",", ":"))
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    return s

if __name__ == "__main__":
    dataset = load_dataset()
    data_str = safe_encode(dataset)

    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PoC Cross-Jurisdiction Privacy Law Compare Demo | Bilingual</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial, sans-serif;}
body{background:#f4f7fb;padding-top:160px;max-width:1400px;margin:0 auto;}
h1{text-align:center;color:#182a46;margin-bottom:8px;font-size:20px;}
.desc{text-align:center;color:#555;margin-bottom:12px;font-size:14px;}

/* 筛选控制栏固定置顶常驻 */
.control-bar{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background:#ffffff;
    padding:16px 22px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.12);
    z-index: 9999;
    display:flex;
    gap:16px;
    align-items:center;
    flex-wrap:wrap;
}

#dimSelect{padding:9px;min-width:220px;border:1px solid #ccd6e0;border-radius:6px;}
#keywordInput{padding:9px;min-width:260px;border:1px solid #ccd6e0;border-radius:6px;}
#refreshBtn{background:#2563eb;color:#fff;border:none;padding:9px 18px;border-radius:6px;cursor:pointer;}
#exportBtn{background:#039674;color:#fff;border:none;padding:9px 18px;border-radius:6px;cursor:pointer;}
.jur-check-group{display:flex;gap:14px;}

.compare-wrap{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin-top:24px;}
.jur-card{background:#fff;border-radius:10px;padding:18px;border:1px solid #e2e8f0;min-height:68vh;overflow-y:auto;}
.card-title{font-size:16px;font-weight:bold;padding-bottom:10px;border-bottom:1px solid #eee;margin-bottom:14px;color:#193677;}
.clause-item{padding:14px 0;border-bottom:1px solid #f0f4fa;}
.clause-id{font-size:12px;color:#777;margin-bottom:8px;}
/* 双语样式区分 */
.original-text{white-space:pre-line;line-height:1.6;font-size:14px;color:#111;}
.en-translate{white-space:pre-line;line-height:1.6;font-size:14px;color:#2358b9;margin-top:10px;border-top:1px dashed #d2dcf0;padding-top:10px;}
.highlight{background:#fff399;padding:0 2px;}
.empty-tip{text-align:center;padding:80px;color:#777;grid-column:1 / -1;font-size:15px;}
.page-bar{margin:26px auto;text-align:center;display:none;}
.page-btn{margin:0 6px;padding:6px 12px;border:1px solid #ccd6e0;background:#fff;border-radius:4px;cursor:pointer;}
.page-btn.active{background:#2563eb;color:#fff;border:#2563eb;}
</style>
</head>
<body>
<!-- 固定置顶筛选区域 -->
<div class="control-bar">
    <div style="width:100%;">
        <h1 style="margin:0;">PoC Multi-Jurisdiction Privacy Clause Side-by-Side Compare</h1>
        <div class="desc">Local Bilingual Dataset | Original Text + Official English Interpretation</div>
    </div>
    <label>Filter by Dimension:</label>
    <select id="dimSelect">
        <option value="">All Dimensions</option>
    </select>
    <label>Keyword:</label>
    <input id="keywordInput" placeholder="Leave empty to show all clauses">
    <div class="jur-check-group">
        <label><input type="checkbox" value="CN_PIPL" checked> CN-PIPL</label>
        <label><input type="checkbox" value="JP_APPI" checked> JP-APPI</label>
        <label><input type="checkbox" value="KR_PIPA" checked> KR-PIPA</label>
    </div>
    <button id="refreshBtn">Refresh Compare Table</button>
    <button id="exportBtn">Export All Bilingual Text</button>
</div>

<div class="compare-wrap" id="compareBox"></div>
<div class="page-bar" id="pageBar"></div>

<script>
const PAGE_SIZE = 8;
let allFiltered = [];
let currentPage = 1;
const rawJsonText = '{{DATA_ESCAPE}}';
const fullData = JSON.parse(rawJsonText);

const dimSelect = document.getElementById("dimSelect");
const keywordInput = document.getElementById("keywordInput");
const refreshBtn = document.getElementById("refreshBtn");
const exportBtn = document.getElementById("exportBtn");
const compareBox = document.getElementById("compareBox");
const pageBar = document.getElementById("pageBar");
const checkboxes = document.querySelectorAll(".jur-check-group input[type=checkbox]");

// 填充维度下拉
const dimOptionsList = [
    "BasicDefinition",
    "DataSubjectRight",
    "DataControllerObligation",
    "AutomatedDecision",
    "MinorProtection",
    "CrossBorderTransfer",
    "Penalty",
    "ComplianceAssessment"
];
dimOptionsList.forEach(d=>{
    const opt = document.createElement("option");
    opt.value = d;
    opt.textContent = d;
    dimSelect.appendChild(opt);
})

refreshBtn.addEventListener("click", runFilter);
exportBtn.addEventListener("click", exportCompareText);

// 过滤逻辑
function runFilter(){
    console.log("Total raw bilingual clauses: ", fullData.length);
    const targetDim = dimSelect.value;
    const kw = keywordInput.value.trim().toLowerCase();
    const selectedJur = [];
    checkboxes.forEach(cb=>{if(cb.checked) selectedJur.push(cb.value);})

    let tempData = [...fullData];
    if(targetDim) tempData = tempData.filter(i=>i.dimension === targetDim);
    tempData = tempData.filter(i=>selectedJur.includes(i.law_code));
    if(kw !== ""){
        tempData = tempData.filter(i=>{
            const ori = i.content_original.toLowerCase();
            const en = i.content_en.toLowerCase();
            return ori.includes(kw) || en.includes(kw);
        });
    }
    allFiltered = tempData;
    currentPage = 1;
    renderCompare();
}

// 三栏并排渲染，每条展示原文+英文释义
function renderCompare(){
    compareBox.innerHTML = "";
    pageBar.style.display = "none";
    const total = allFiltered.length;
    if(total === 0){
        compareBox.innerHTML = `<div class="empty-tip">No matching bilingual clauses, restore all filters to default.</div>`;
        return;
    }
    const groupCN = allFiltered.filter(i=>i.law_code === "CN_PIPL");
    const groupJP = allFiltered.filter(i=>i.law_code === "JP_APPI");
    const groupKR = allFiltered.filter(i=>i.law_code === "KR_PIPA");
    const kw = keywordInput.value.trim();

    function buildCard(title, arr){
        let html = `<div class="jur-card"><div class="card-title">${title}</div>`;
        arr.forEach(item=>{
            let oriText = item.content_original;
            let enText = item.content_en;
            if(kw){
                const reg = new RegExp(`(${kw})`, "gi");
                oriText = oriText.replace(reg, `<span class="highlight">$1</span>`);
                enText = enText.replace(reg, `<span class="highlight">$1</span>`);
            }
            html += `
                <div class="clause-item">
                    <div class="clause-id">${item.clause_no} | ${item.dimension}</div>
                    <div class="original-text">Original: ${oriText}</div>
                    <div class="en-translate">Official English Interpretation: ${enText}</div>
                </div>
            `;
        })
        html += "</div>";
        return html;
    }
    compareBox.innerHTML = buildCard("CN-PIPL (China)", groupCN)
        + buildCard("JP-APPI (Japan)", groupJP)
        + buildCard("KR-PIPA (Korea)", groupKR);
}

// 导出全部双语文本
function exportCompareText(){
    let out = "==== Multi-Jurisdiction Bilingual Compare Export ====\\n\\n";
    fullData.forEach(item=>{
        out += `[${item.law_code}] ${item.clause_no} [${item.dimension}]\\nOriginal: ${item.content_original}\\nEnglish: ${item.content_en}\\n\\n`;
    })
    navigator.clipboard.writeText(out).then(()=>alert("All bilingual clauses copied to clipboard!"));
}

// 页面加载自动刷新展示全部法条
window.onload = function(){
    runFilter();
}
</script>
</body>
</html>
'''
    final_html = html_template.replace("{{DATA_ESCAPE}}", data_str)
    output_html = os.path.join(HTML_OUT, "PoC_Cross_Jurisdiction_Compare.html")
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("✅ PoC_Cross_Jurisdiction_Compare.html generated complete")
    print(f"Output Path: {output_html}")
    print("Feature List:")
    print("1. Fixed top filter bar, always visible when scroll")
    print("2. Bilingual display: Original Text + Official English Interpretation")
    print("3. Keyword highlight both in original and English content")
    print("4. Export full bilingual text to clipboard")
    print("5. Pure offline static page, no CORS / API error")
''
