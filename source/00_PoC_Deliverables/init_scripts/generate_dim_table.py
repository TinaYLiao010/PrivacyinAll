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
    return data

# 下拉选项HTML
def build_options():
    opt = '<option value="all">All Dimensions (Show All)</option>\n'
    for d in DIM_LIST:
        opt += f'        <option value="{d}">{d}</option>\n'
    return opt

# JSON安全转义
def safe_json_dump(data):
    raw = json.dumps(data, ensure_ascii=False)
    raw = raw.replace("\\", "\\\\").replace("'", "\\'")
    return raw

if __name__ == "__main__":
    dataset = load_dataset()
    total = len(dataset)
    print(f"✅ 读取法条总数：{total}")
    if total == 0:
        print("⚠️ json为空，表格会空白，请重新运行步骤3")

    option_html = build_options()
    js_str = safe_json_dump(dataset)

    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PoC Dimension Classification Table</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:Arial;padding:24px;background:#f3f6f9;}
h1{text-align:center;color:#1d2b41;margin-bottom:10px;}
.desc{text-align:center;color:#555;margin-bottom:24px;font-size:14px;}
.filter-bar{background:#fff;padding:16px;border-radius:8px;margin-bottom:20px;display:flex;gap:12px;align-items:center;}
#dimSelect{width:320px;padding:6px;font-size:14px;}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;}
thead tr{background:#2c4b82;color:#fff;}
th,td{padding:12px 14px;border:1px solid #e2e8f0;text-align:left;font-size:14px;}
.col-code{width:10%;}
.col-clause{width:12%;}
.col-dim{width:14%;}
.col-text{width:64%;}
tr:hover{background:#f7faff;}
.empty-tip{padding:40px;text-align:center;color:#888;font-size:15px;}
</style>
</head>
<body>
<h1>PoC Law Clause Dimension Classification Table</h1>
<div class="desc">Source: poc_sample_law_dataset.json | Static Offline Page</div>
<div class="filter-bar">
<label>Filter Dimension:</label>
<select id="dimSelect">
{{OPTION_HTML}}
</select>
</div>
<table>
<thead>
<tr>
<th class="col-code">Law Code</th>
<th class="col-clause">Clause ID</th>
<th class="col-dim">Dimension Tag</th>
<th class="col-text">Original Text</th>
</tr>
</thead>
<tbody id="tableBody"></tbody>
</table>

<script>
const fullDataset = JSON.parse('{{JS_DATA}}');
const tableBody = document.getElementById('tableBody');
const selector = document.getElementById('dimSelect');

function render(filterDim){
    tableBody.innerHTML = "";
    let list;
    if(filterDim === "all"){
        list = fullDataset;
    }else{
        list = fullDataset.filter(item => item.dimension === filterDim);
    }
    if(list.length === 0){
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = 4;
        td.className = "empty-tip";
        td.innerText = "No matching clauses under this dimension.";
        tr.appendChild(td);
        tableBody.appendChild(tr);
        return;
    }
    list.forEach(item=>{
        const tr = document.createElement("tr");
        let text = item.content_original.replaceAll("\\n", "<br>");
        tr.innerHTML = `
            <td>${item.law_code}</td>
            <td>${item.clause_no}</td>
            <td>${item.dimension}</td>
            <td style="white-space:pre-line;">${text}</td>
        `;
        tableBody.appendChild(tr);
    })
}
render("all");
selector.onchange = function(){
    render(this.value);
}
</script>
</body>
</html>
'''
    final_html = html_template.replace("{{OPTION_HTML}}", option_html)
    final_html = final_html.replace("{{JS_DATA}}", js_str)

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"✅ 页面生成成功：{output_html}")