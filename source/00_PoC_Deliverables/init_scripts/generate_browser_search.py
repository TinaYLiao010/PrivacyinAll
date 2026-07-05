import os
import json

base_path = os.path.abspath(os.path.dirname(__file__))
DATA_JSON = os.path.join(base_path, "../poc_sample_datasets/poc_sample_law_dataset.json")
HTML_OUT = os.path.join(base_path, "../poc_visual_demos")

# 创建文件夹，兼容无exist_ok
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

def load_law_dataset():
    if not os.path.exists(DATA_JSON):
        print(f"Error: Missing {DATA_JSON}, run PoC Step3 first!")
        exit(1)
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded total bilingual clauses: {len(data)}")
    return data

# 多层安全转义，消除JS SyntaxError
def safe_encode_json(raw):
    s = json.dumps(raw, ensure_ascii=False, separators=(",", ":"))
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    return s

if __name__ == "__main__":
    dataset = load_law_dataset()
    data_str = safe_encode_json(dataset)

    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PoC Offline Law Search Demo | Bilingual Original + English</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial, sans-serif;}
body{background:#f4f7fc;padding:20px;max-width:1200px;margin:0 auto;}
h1{text-align:center;color:#172b47;margin-bottom:10px;}
.desc{text-align:center;color:#666;margin-bottom:24px;font-size:14px;}
.search-bar{background:#fff;padding:18px;border-radius:8px;margin-bottom:20px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;box-shadow:0 1px 6px #e1e6f0;}
#dimFilter{padding:9px;min-width:220px;border:1px solid #ccd6e0;border-radius:6px;}
#jurFilter{padding:9px;min-width:180px;border:1px solid #ccd6e0;border-radius:6px;}
#keywordInput{padding:9px;flex:1;min-width:280px;border:1px solid #ccd6e0;border-radius:6px;}
#searchBtn{background:#2563eb;color:#fff;border:none;padding:9px 16px;border-radius:6px;cursor:pointer;}
#resetBtn{background:#6b7280;color:#fff;border:none;padding:9px 16px;border-radius:6px;cursor:pointer;}
.result-box{background:#fff;border-radius:10px;padding:20px;min-height:60vh;overflow-y:auto;}
.clause-card{border-bottom:1px solid #e9edf7;padding:16px 0;}
.card-header{font-size:13px;color:#555;margin-bottom:8px;}
.original-text{line-height:1.6;margin-bottom:10px;white-space:pre-line;}
.en-trans-text{line-height:1.6;color:#2563eb;border-top:1px dashed #d0d9ec;padding-top:10px;white-space:pre-line;}
.highlight{background:#fff299;padding:0 2px;}
.empty-tip{text-align:center;padding:80px;color:#777;font-size:15px;}
.page-control{margin-top:20px;text-align:center;display:none;}
.page-btn{margin:0 6px;padding:6px 12px;border:1px solid #ccd6e0;background:#fff;border-radius:4px;cursor:pointer;}
.page-btn.active{background:#2563eb;color:#fff;border:#2563eb;}
</style>
</head>
<body>
<h1>PoC Multi-Jurisdiction Privacy Law Search</h1>
<div class="desc">Local Bilingual Dataset | Original Text + Official English Interpretation</div>

<div class="search-bar">
    <label>Filter Dimension:</label>
    <select id="dimFilter">
        <option value="">All Dimensions</option>
    </select>
    <label>Jurisdiction:</label>
    <select id="jurFilter">
        <option value="">All Jurisdictions</option>
        <option value="CN_PIPL">CN-PIPL</option>
        <option value="JP_APPI">JP-APPI</option>
        <option value="KR_PIPA">KR-PIPA</option>
    </select>
    <input id="keywordInput" placeholder="Input keyword to highlight (bilingual match)">
    <button id="searchBtn">Search</button>
    <button id="resetBtn">Reset All Filters</button>
</div>

<div class="result-box" id="resultBox"></div>
<div class="page-control" id="pageBar"></div>

<script>
const PAGE_SIZE = 10;
let fullLawData = JSON.parse('{{DATA_STR}}');
let filteredList = [];
let currentPage = 1;

const dimFilter = document.getElementById("dimFilter");
const jurFilter = document.getElementById("jurFilter");
const keywordInput = document.getElementById("keywordInput");
const searchBtn = document.getElementById("searchBtn");
const resetBtn = document.getElementById("resetBtn");
const resultBox = document.getElementById("resultBox");
const pageBar = document.getElementById("pageBar");

// 填充维度下拉
const dimList = [
    "BasicDefinition",
    "DataSubjectRight",
    "DataControllerObligation",
    "AutomatedDecision",
    "MinorProtection",
    "CrossBorderTransfer",
    "Penalty",
    "ComplianceAssessment"
];
dimList.forEach(d=>{
    const opt = document.createElement("option");
    opt.value = d;
    opt.textContent = d;
    dimFilter.appendChild(opt);
})

// 绑定按钮事件
searchBtn.addEventListener("click", doSearch);
resetBtn.addEventListener("click", resetAll);
keywordInput.addEventListener("keydown", e=>{if(e.key === "Enter") searchBtn.click();})

// 重置所有筛选条件
function resetAll(){
    dimFilter.value = "";
    jurFilter.value = "";
    keywordInput.value = "";
    filteredList = [...fullLawData];
    currentPage = 1;
    renderPage();
}

// 核心筛选逻辑
function doSearch(){
    const dimVal = dimFilter.value;
    const jurVal = jurFilter.value;
    const kw = keywordInput.value.trim().toLowerCase();
    filteredList = [...fullLawData];

    if(dimVal) filteredList = filteredList.filter(item => item.dimension === dimVal);
    if(jurVal) filteredList = filteredList.filter(item => item.law_code === jurVal);
    if(kw){
        filteredList = filteredList.filter(item=>{
            const ori = item.content_original.toLowerCase();
            const en = item.content_en.toLowerCase();
            return ori.includes(kw) || en.includes(kw);
        })
    }
    currentPage = 1;
    renderPage();
}

// 关键词高亮处理
function highlightText(text, kw){
    if(!kw) return text;
    const reg = new RegExp(`(${kw})`, "gi");
    return text.replace(reg, `<span class="highlight">$1</span>`);
}

// 分页渲染双语法条（原文+英文释义）
function renderPage(){
    resultBox.innerHTML = "";
    pageBar.style.display = "none";
    const total = filteredList.length;
    if(total === 0){
        resultBox.innerHTML = `<div class="empty-tip">No matching bilingual clauses found, adjust filters or keyword.</div>`;
        return;
    }
    // 分页切片
    const totalPage = Math.ceil(total / PAGE_SIZE);
    const start = (currentPage - 1) * PAGE_SIZE;
    const pageData = filteredList.slice(start, start + PAGE_SIZE);
    const kw = keywordInput.value.trim();

    // 渲染每条双语卡片
    pageData.forEach(item=>{
        const oriHtml = highlightText(item.content_original, kw);
        const enHtml = highlightText(item.content_en, kw);
        const card = `
        <div class="clause-card">
            <div class="card-header">[${item.law_code}] ${item.clause_no} | Dimension: ${item.dimension}</div>
            <div class="original-text"><b>Original Text:</b><br>${oriHtml}</div>
            <div class="en-trans-text"><b>Official English Interpretation:</b><br>${enHtml}</div>
        </div>
        `;
        resultBox.innerHTML += card;
    })

    // 生成分页按钮
    if(totalPage > 1){
        pageBar.style.display = "block";
        pageBar.innerHTML = "";
        for(let i=1;i<=totalPage;i++){
            const btn = document.createElement("button");
            btn.className = "page-btn" + (i === currentPage ? " active" : "");
            btn.textContent = i;
            btn.onclick = ()=>{
                currentPage = i;
                renderPage();
            }
            pageBar.appendChild(btn);
        }
    }
}

// 页面加载默认展示全部法条
window.onload = ()=>{
    filteredList = [...fullLawData];
    renderPage();
}
</script>
</body>
</html>
'''
    final_html = html_template.replace("{{DATA_STR}}", data_str)
    output_html = os.path.join(HTML_OUT, "PoC_Search_Demo.html")
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("✅ PoC_Search_Demo.html generated complete")
    print(f"File Path: {output_html}")
    print("Feature Update:")
    print("1. Bilingual display: Original Text + Official English Interpretation")
    print("2. Keyword highlight both in original and English text")
    print("3. Pure offline static page, no CORS / API request")
    print("4. Pagination, dimension & jurisdiction filter")