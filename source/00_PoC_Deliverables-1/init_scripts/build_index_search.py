import os
import json

# 脚本自身路径
base_path = os.path.abspath(os.path.dirname(__file__))
# 结构化数据集路径
DATA_JSON_PATH = os.path.join(base_path, "../poc_sample_datasets/poc_sample_law_dataset.json")
# HTML输出目录
HTML_OUT_DIR = os.path.join(base_path, "../poc_visual_demos")

# 兼容低版本Python，不使用exist_ok
if not os.path.exists(HTML_OUT_DIR):
    os.makedirs(HTML_OUT_DIR)

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
# 三大法域
JURIS_LIST = ["CN_PIPL", "JP_APPI", "KR_PIPA"]

# 加载步骤3生成的法条数据集
def load_law_dataset():
    if not os.path.exists(DATA_JSON_PATH):
        print(f"【错误】未找到数据集：{DATA_JSON_PATH}")
        print("请先运行 poc_struct_generator.py 生成 poc_sample_law_dataset.json")
        exit(1)
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ 成功读取法条总条数：{len(data)}")
    return data

# 安全转义JSON，防止前端JS解析崩溃
def safe_json_encode(raw_data):
    json_str = json.dumps(raw_data, ensure_ascii=False, separators=(",", ":"))
    json_str = json_str.replace("\\", "\\\\").replace("'", "\\'")
    return json_str

if __name__ == "__main__":
    # 读取数据集
    dataset = load_law_dataset()
    dataset_escaped = safe_json_encode(dataset)

    # 生成法域下拉选项
    jur_options = '<option value="all">All Jurisdictions</option>\n'
    for jur in JURIS_LIST:
        jur_options += f'        <option value="{jur}">{jur}</option>\n'

    # 生成维度下拉选项
    dim_options = '<option value="all">All Dimensions</option>\n'
    for dim in DIM_LIST:
        dim_options += f'        <option value="{dim}">{dim}</option>\n'

    # 完整静态检索页面模板（JS逻辑全部修复）
    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PoC Offline Full Text Search Demo</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial, Helvetica, sans-serif;}
body{background:#f4f7fb;padding:24px;}
h1{text-align:center;color:#192a46;margin-bottom:12px;}
.desc{text-align:center;color:#555;margin-bottom:30px;font-size:14px;}
.search-bar{background:#fff;padding:20px;border-radius:10px;max-width:1200px;margin:0 auto 24px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;}
.search-bar input{flex:1;min-width:300px;padding:9px 12px;font-size:15px;border:1px solid #ccd6e0;border-radius:6px;}
.search-bar select{padding:9px 10px;font-size:14px;border:1px solid #ccd6e0;border-radius:6px;min-width:200px;}
#searchBtn{background:#2554b8;color:white;border:none;padding:9px 22px;border-radius:6px;cursor:pointer;font-size:14px;}
#searchBtn:hover{background:#1d4499;}
.result-wrap{max-width:1200px;margin:0 auto;}
.result-item{background:#fff;padding:18px;border-radius:8px;margin-bottom:16px;border:1px solid #e2e8f0;}
.item-head{display:flex;gap:16px;margin-bottom:10px;flex-wrap:wrap;}
.tag-jur{background:#e6f0ff;color:#1b58b3;padding:4px 10px;border-radius:20px;font-size:13px;}
.tag-dim{background:#e8f9f2;color:#0e7850;padding:4px 10px;border-radius:20px;font-size:13px;}
.clause-id{color:#666;font-size:13px;}
.content-text{white-space:pre-line;margin-top:12px;line-height:1.7;color:#222;}
.highlight{background:#fff299;padding:0 3px;}
.empty-tip{text-align:center;padding:60px;color:#777;font-size:16px;}
.page-bar{max-width:1200px;margin:20px auto;text-align:center;display:none;}
.page-btn{margin:0 6px;padding:6px 12px;border:1px solid #cbd5e0;background:#fff;border-radius:4px;cursor:pointer;}
.page-btn.active{background:#2554b8;color:white;border:#2554b8;}
</style>
</head>
<body>
<h1>PoC Offline Full Text Search Demo</h1>
<div class="desc">Static Frontend Filter | Jurisdiction + Dimension Filter | Keyword Highlight</div>
<div class="search-bar">
    <input id="keywordInput" placeholder="Leave empty to show all clauses">
    <select id="jurSelect">
        {{JUR_OPTION_HTML}}
    </select>
    <select id="dimSelect">
        {{DIM_OPTION_HTML}}
    </select>
    <button id="searchBtn">Search</button>
</div>
<div class="result-wrap" id="resultBox"></div>
<div class="page-bar" id="pageBar"></div>

<script>
const PAGE_SIZE = 10;
let allResults = [];
let currentPage = 1;

// 安全解析注入的完整法条数据
const rawJsonText = '{{DATA_ESCAPE_STR}}';
const fullDataset = JSON.parse(rawJsonText);

// DOM元素
const keywordInput = document.getElementById("keywordInput");
const jurSelect = document.getElementById("jurSelect");
const dimSelect = document.getElementById("dimSelect");
const searchBtn = document.getElementById("searchBtn");
const resultBox = document.getElementById("resultBox");
const pageBar = document.getElementById("pageBar");

// 绑定搜索事件
searchBtn.addEventListener("click", runSearch);
keywordInput.addEventListener("keydown", function(e){
    if(e.key === "Enter") runSearch();
})

// 检索过滤主逻辑
function runSearch(){
    const kw = keywordInput.value.trim().toLowerCase();
    const targetJur = jurSelect.value;
    const targetDim = dimSelect.value;

    // 拷贝原始数据，不污染源数组
    let filterData = [...fullDataset];

    // 法域过滤
    if(targetJur !== "all"){
        filterData = filterData.filter(item => item.law_code === targetJur);
    }
    // 维度过滤
    if(targetDim !== "all"){
        filterData = filterData.filter(item => item.dimension === targetDim);
    }
    // 关键词模糊匹配
    if(kw !== ""){
        filterData = filterData.filter(item => item.content_original.toLowerCase().includes(kw));
    }

    allResults = filterData;
    currentPage = 1;
    renderTable();
}

// 分页渲染函数
function renderTable(){
    resultBox.innerHTML = "";
    pageBar.style.display = "none";
    const total = allResults.length;

    if(total === 0){
        resultBox.innerHTML = `<div class="empty-tip">No matching clauses found, adjust your filters or keywords.</div>`;
        return;
    }

    const totalPage = Math.ceil(total / PAGE_SIZE);
    const startIdx = (currentPage - 1) * PAGE_SIZE;
    const pageSlice = allResults.slice(startIdx, startIdx + PAGE_SIZE);

    // 渲染每条法条卡片
    pageSlice.forEach(item => {
        let textContent = item.content_original;
        const kw = keywordInput.value.trim();
        if(kw){
            const reg = new RegExp(`(${kw})`, "gi");
            textContent = textContent.replace(reg, `<span class="highlight">$1</span>`);
        }
        const itemHtml = `
            <div class="result-item">
                <div class="item-head">
                    <span class="tag-jur">${item.law_code}</span>
                    <span class="tag-dim">${item.dimension}</span>
                    <span class="clause-id">Clause ID: ${item.clause_no}</span>
                </div>
                <div class="content-text">${textContent}</div>
            </div>
        `;
        resultBox.innerHTML += itemHtml;
    })

    // 生成分页按钮
    if(totalPage > 1){
        pageBar.style.display = "block";
        let pageHtml = "";
        for(let p=1; p<=totalPage; p++){
            pageHtml += `<button class="page-btn ${p === currentPage ? 'active' : ''}" onclick="switchPage(${p})">${p}</button>`
        }
        pageBar.innerHTML = pageHtml;
    }
}

// 切换分页
function switchPage(p){
    currentPage = p;
    renderTable();
}

// 页面加载自动执行一次，展示全部数据
window.onload = function(){
    runSearch();
}
</script>
</body>
</html>
'''
    # 填充模板占位符
    final_html = html_template.replace("{{JUR_OPTION_HTML}}", jur_options)
    final_html = final_html.replace("{{DIM_OPTION_HTML}}", dim_options)
    final_html = final_html.replace("{{DATA_ESCAPE_STR}}", dataset_escaped)

    # 写入HTML文件
    output_html_path = os.path.join(HTML_OUT_DIR, "PoC_Search_Demo.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("✅ PoC_Search_Demo.html 生成完成")
    print(f"文件路径：{output_html_path}")
    print("使用说明：打开页面自动加载全部法条，清空关键词+全部下拉选All即可验证数据正常")